# Code Review — ElGamal Prototype

**Reviewer:** Claude
**Người được review:** Trung
**File được review:** `elgamal.py`, `demo.py`
**Ngày:** 09/05/2026

---

## 1. Tổng quan

Đoạn code triển khai chính xác sơ đồ chữ ký ElGamal cổ điển. Test demo
pass cả 5 trường hợp ở `p = 1024-bit`. Kiến trúc rõ ràng, có docstring,
kiểu dữ liệu được khai báo bằng `Tuple[...]`. Phần dưới đây ghi lại
những điểm đã đúng và những điểm cần cải tiến.

**Mức độ nghiêm trọng được đánh dấu:**

- 🔴 **Critical** — phải sửa nếu định dùng trong môi trường có rủi ro
- 🟠 **Important** — sửa để cải thiện chất lượng / đúng đắn
- 🟢 **Nit** — góp ý nhỏ

---

## 2. Những điểm đã làm tốt ✅

| # | Mục | Ghi chú |
|---|---|---|
| 1 | Dùng `secrets` chứ không phải `random` | Đúng chuẩn cho dữ liệu mật |
| 2 | Dùng safe prime `p = 2q + 1` | Loại bỏ rủi ro nhóm con nhỏ |
| 3 | Kiểm tra `g² ≢ 1` và `g^q ≢ 1` để xác minh `ord(g) = 2q` | Logic toán học chính xác |
| 4 | `Verify` kiểm tra `0 < r < p` và `0 < s < p − 1` | Phòng tấn công Bleichenbacher 1996 trên ElGamal |
| 5 | Tách `_hash_to_int` thành hàm riêng | Dễ thay hash function khác |
| 6 | Sàng nhanh bằng `_SMALL_PRIMES` trước Miller–Rabin | Tăng tốc rõ rệt cho safe prime |
| 7 | Vòng `while True` ở `sign()` lặp lại nếu `s == 0` | Đúng theo đặc tả |
| 8 | Test phát hiện cả văn bản giả mạo lẫn chữ ký giả mạo | Coverage tốt |

---

## 3. Issues phải xem xét

### 🔴 #1 — Không an toàn trước **timing attack** trên `pow(...)` và so sánh

Hàm `verify` kết thúc bằng `return lhs == rhs`. So sánh số nguyên Python
**không phải hằng-thời-gian**: `==` thoát sớm khi gặp digit khác nhau.
`pow(base, exp, mod)` cũng không hằng-thời-gian theo `exp`.

Trong sign, `pow(g, k, p)` chạy với `k` bí mật → thời gian rò rỉ thông
tin về `k` → có thể khôi phục `x`.

**Đề xuất.**
- Đối với prototype học tập, ghi rõ trong docstring.
- Nếu muốn tiến gần production: dùng `gmpy2.powmod_sec` hoặc
  `Crypto.Util.number.long_to_bytes` + so sánh hằng-thời-gian
  `hmac.compare_digest`.

```python
import hmac
return hmac.compare_digest(lhs.to_bytes(...), rhs.to_bytes(...))
```

---

### 🔴 #2 — `k` được sinh trong `[2, p−2]` nhưng exponent là **`mod (p − 1)`**

`k` đang được lấy từ `[2, p − 2]`, kích thước cỡ `p`. Nhưng `s` được
tính trong `Z_{p-1}`, tức là chỉ phần `k mod (p−1)` mới có ý nghĩa.

Hệ quả:
- Một nửa các giá trị `k` trong `[2, p−2]` bị bỏ qua bởi check
  `gcd(k, p − 1) == 1` (vì `p − 1 = 2q`, nên `k` chẵn → loại; khoảng
  một nửa bị loại).
- Phân phối của `k mod (p − 1)` không đều **một cách hoàn hảo** vì khoảng
  `[2, p − 2]` không phải bội số nguyên của `p − 1`.

**Đề xuất.**
```python
# Đúng hơn:
k = secrets.randbelow(p - 3) + 2          # [2, p-2]
# nên đổi thành:
k = secrets.randbelow(p - 3) + 2          # OK về phạm vi
# hoặc tốt hơn: lấy trực tiếp trong [2, p-2] nhưng lưu ý gcd với (p-1)
```

Phạm vi hiện tại không sai về mặt đúng-đắn (chữ ký vẫn verify), nhưng
nhỏ hơn `p − 1` chút và phân phối hơi lệch. Đối với prototype 1024-bit
độ lệch không khai thác được, **nhưng cần ghi chú**.

---

### 🟠 #3 — `secrets.randbelow(p - 3) + 2` là pattern dễ sai

Biểu thức `randbelow(n)` trả về `[0, n − 1]`. Cộng `+ 2` cho `[2, n + 1]`.
Với `n = p − 3` ⇒ `[2, p − 2]`. Đúng. Nhưng dòng này xuất hiện ở **3 chỗ
khác nhau** trong codebase (`find_primitive_root`, `keygen`, `sign`),
mỗi chỗ một biến thể (`p−2`, `p−3`).

**Đề xuất.** Trích thành helper:

```python
def _random_in_range(low: int, high: int) -> int:
    """Trả về số ngẫu nhiên trong [low, high] (đóng cả 2 đầu)."""
    return secrets.randbelow(high - low + 1) + low
```

Rồi gọi `_random_in_range(2, p - 2)`. Code đọc rõ ràng, ít bug nhất.

---

### 🟠 #4 — `_hash_to_int` rút gọn hash quá thô

Hiện tại: `int.from_bytes(SHA256(m), "big") % (p − 1)`.

- Với `p` 1024-bit, hash 256-bit luôn `< p − 1`, mod là vô nghĩa nhưng
  vô hại.
- Với `p` 512-bit, hash 256-bit có thể lớn hơn hoặc gần `p − 1`, mod
  gây bias rất nhỏ.
- Quan trọng hơn: **không có domain separation**. Nếu sau này code dùng
  cùng SHA-256 cho mục đích khác (ví dụ băm khoá phiên), có thể bị
  cross-protocol attack.

**Đề xuất.** Thêm prefix domain separator:

```python
def _hash_to_int(message: bytes, modulus: int) -> int:
    digest = hashlib.sha256(b"ElGamal-Sign-v1\x00" + message).digest()
    return int.from_bytes(digest, "big") % modulus
```

---

### 🟠 #5 — `find_primitive_root` không xử lý trường hợp `p = 3`

Với `p = 3, q = 1`, vòng lặp sẽ lặp vô hạn vì `q = 1` không phải
nguyên tố — nhưng `generate_safe_prime(2)` đã chặn bằng
`if bits < 16`. **Hiện tại an toàn**, nhưng nếu sau này ai gọi trực
tiếp `find_primitive_root(p, q)` với cặp lạ, có thể treo.

**Đề xuất.** Thêm assert ở đầu hàm:

```python
assert p == 2 * q + 1 and isPrime(q) and isPrime(p), \
    "Cần p = 2q + 1 với cả hai nguyên tố"
```

---

### 🟠 #6 — `sign()` không kiểm tra `r != 0`

Theo lý thuyết, `r = g^k mod p` không bao giờ bằng 0 vì `g, k > 0`,
nhưng nếu trong tương lai code đổi sang nhóm con khác (ví dụ trên
elliptic curve), điều này không còn đúng. Thêm `if r == 0: continue`
là practice phòng thủ tốt.

---

### 🟢 #7 — Có thể khai thác song song khi sinh safe prime

`generate_safe_prime` chạy tuần tự. Trên CPU đa nhân, có thể chạy
nhiều worker cùng lúc và lấy kết quả đầu tiên. Với `bits = 2048`
(nếu mở rộng đề tài), điều này tiết kiệm đáng kể.

```python
from concurrent.futures import ProcessPoolExecutor, FIRST_COMPLETED, wait
# pseudo-code: chia worker, return prime đầu tiên tìm được
```

Không bắt buộc cho 1024-bit (~30s).

---

### 🟢 #8 — Demo dùng `assert` cho test

`demo.py` dùng `assert ok, "..."`. Khi chạy với `python -O demo.py`,
các `assert` bị **loại bỏ hoàn toàn** → test sẽ luôn pass kể cả khi
sai. Không nghiêm trọng vì đây là demo, nhưng nếu chuyển sang dạng
test thật:

```python
if not ok:
    raise SystemExit("Chữ ký không hợp lệ với văn bản gốc!")
```

Hoặc viết bằng `pytest`.

---

### 🟢 #9 — Type hints có thể chặt hơn

`PublicKey = Tuple[int, int, int]` đúng nhưng không phân biệt được
`(p, g, y)` với `(r, s, x)`. Nếu lỡ truyền sai thứ tự arg, mypy
không bắt được. Có thể dùng `NamedTuple`:

```python
from typing import NamedTuple

class PublicKey(NamedTuple):
    p: int
    g: int
    y: int

class Signature(NamedTuple):
    r: int
    s: int
```

Đọc code dễ hơn nhiều. Trade-off: phải đổi `public_key[0]` thành
`public_key.p`.

---

## 4. Kiểm tra toán học (sanity check)

Tôi đã verify thủ công công thức trong `verify`:

Cho `(r, s) = sign(m)`:
- `s = (h − xr) · k⁻¹  (mod p − 1)`
- `s · k ≡ h − xr      (mod p − 1)`
- `xr + sk ≡ h          (mod p − 1)`

Lên mũ với cơ số `g`, dùng định lý Fermat nhỏ (`g^(p−1) ≡ 1 mod p`):

- `g^(xr) · g^(sk) ≡ g^h   (mod p)`
- `(g^x)^r · (g^k)^s ≡ g^h (mod p)`
- `y^r · r^s ≡ g^h         (mod p)` ✓

Khớp với cài đặt trong `verify`. **Code đúng về mặt toán học.**

---

## 5. Tóm tắt đề xuất ưu tiên

| # | Mức | Việc cần làm |
|---|---|---|
| 1 | 🟠 #3 | Trích `_random_in_range` để giảm dup |
| 2 | 🟠 #4 | Thêm domain separator cho hash |
| 3 | 🟠 #5 | Thêm assert cho `find_primitive_root` |
| 4 | 🟠 #6 | Thêm check `r != 0` trong `sign` |
| 5 | 🟢 #9 | Đổi sang `NamedTuple` cho readability |
| 6 | 🔴 #1, #2 | **Ghi chú vào README** rằng prototype không chống timing attack |

Sửa theo thứ tự trên thì code vừa sạch hơn, vừa đầy đủ caveat học thuật,
mà không làm phình logic chính.

---

## 6. Kết luận

Prototype **đạt yêu cầu đề bài**: KeyGen / Sign / Verify hoạt động chính
xác với `p = 1024-bit`, ký và verify thành công văn bản mẫu, phát hiện
được giả mạo cả ở văn bản lẫn chữ ký. Toán học khớp với đặc tả gốc của
ElGamal 1985. Các điểm yếu còn lại đều là về *production-hardening*
(timing, encoding, side-channel) — nằm ngoài phạm vi của một prototype
học tập, nhưng nên ghi chú để tránh nhầm lẫn nếu có ai re-use code này.

**Đề xuất bước tiếp theo cho đồ án:**
1. Mở rộng sang **DSA** (sign trên nhóm con cấp `q`, exponent `mod q`)
   và so sánh kích thước chữ ký.
2. Nghiên cứu **forking lemma** / chứng minh an toàn của ElGamal trong
   ROM (Random Oracle Model).
3. Cài thử **ECElGamal** trên đường cong elliptic để thấy lợi thế kích
   thước khoá.
