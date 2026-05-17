# ElGamal Digital Signature — Prototype

> Triển khai sơ đồ chữ ký số ElGamal (1985) cho mục đích học tập.
> Bài tập / đồ án — Trung, Toán-Tin K68, HUST.

## 1. Mô tả

Prototype này hiện thực ba nguyên thuỷ của sơ đồ chữ ký ElGamal:

- **`KeyGen(bits)`** — sinh `(p, g, y)` công khai và `x` bí mật, trong đó
  `p` là **safe prime** (`p = 2q + 1`, `q` cũng nguyên tố) và `g` là
  **căn nguyên thuỷ** modulo `p`.
- **`Sign(m)`** — ký thông điệp `m` (bytes), trả về chữ ký `(r, s)`.
- **`Verify(m, (r, s))`** — kiểm tra `g^h ≡ y^r · r^s  (mod p)` với
  `h = SHA-256(m) mod (p − 1)`.

Có thể chạy với `p` 512-bit (thử nghiệm nhanh) hoặc **1024-bit** (mặc định
theo yêu cầu đề bài).

## 2. Cấu trúc thư mục

```
elgamal_prototype/
├── elgamal.py         # Triển khai KeyGen / Sign / Verify
├── demo.py            # Script chạy thử end-to-end
├── requirements.txt   # Phụ thuộc Python
├── README.md          # Tài liệu này
└── CODE_REVIEW.md     # Bản review chi tiết của prototype
```

## 3. Cài đặt môi trường

Yêu cầu Python ≥ **3.8** (vì code dùng `pow(k, -1, n)` để tính nghịch đảo).

```bash
# 1. Tạo virtualenv (khuyến nghị)
python3 -m venv .venv
source .venv/bin/activate           # Linux/macOS
# .venv\Scripts\activate            # Windows PowerShell

# 2. Cài phụ thuộc
pip install -r requirements.txt
```

Phụ thuộc duy nhất là `pycryptodome` — chỉ dùng nó cho **`getPrime`** và
**`isPrime`** (sinh số nguyên tố lớn + Miller–Rabin). Toàn bộ logic
ElGamal được viết tay từ đầu.

## 4. Chạy demo

```bash
# Chạy với p = 1024-bit (mặc định, theo yêu cầu)
python demo.py

# Chạy nhanh với p = 512-bit (kiểm tra logic)
python demo.py --bits 512

# Đổi thông điệp ký
python demo.py --message "Hop dong so 42, ky ngay 09/05/2026"
```

Demo sẽ thực hiện 5 bước:

1. Sinh cặp khoá `(p, g, y)` / `x`.
2. Ký một văn bản mẫu, in ra `(r, s)`.
3. Xác thực chữ ký với **văn bản gốc** → phải trả về **HỢP LỆ**.
4. Xác thực chữ ký với **văn bản bị sửa** → phải trả về **KHÔNG HỢP LỆ**.
5. Xác thực **chữ ký bị thay đổi** (`s + 1`) → phải trả về **KHÔNG HỢP LỆ**.

### Kết quả chạy mẫu (1024-bit)

```
================================================================
 ElGamal Digital Signature — Prototype Demo  (p = 1024-bit)
================================================================

[1] Sinh cặp khoá …
    Hoàn tất sau 22.22s (p có 1024 bit)
    ...
[2] Văn bản cần ký: 'Day la van ban mau de ky bang ElGamal. Trung — HUST, Toan-Tin.'
    Đang ký …
    Hoàn tất sau 5.2 ms
[3] Xác thực chữ ký với văn bản gốc …
    Kết quả: HỢP LỆ ✓
[4] Xác thực chữ ký trên văn bản đã bị sửa …
    Kết quả: KHÔNG HỢP LỆ ✗  (đúng)
[5] Xác thực chữ ký bị thay đổi (s + 1) …
    Kết quả: KHÔNG HỢP LỆ ✗  (đúng)

 Tất cả kiểm tra đã PASS.
```

> **Ghi chú thời gian.** Sinh safe prime 1024-bit thường mất **20–90 giây**
> tuỳ vận may (cần tìm cặp `(q, 2q+1)` đều nguyên tố). Ký ≈ 5 ms, xác thực
> ≈ 10 ms — chi phí chính ở `pow(g, k, p)`, `pow(y, r, p)`, `pow(r, s, p)`.

## 5. API tóm tắt

```python
from elgamal import keygen, sign, verify

(p, g, y), x = keygen(bits=1024)        # sinh khoá

msg = b"Van ban can ky"
r, s = sign(msg, (p, g, y), x)          # ký

assert verify(msg, (r, s), (p, g, y))   # xác thực
```

## 6. Cảnh báo bảo mật

Đây là **prototype học tập**. **KHÔNG** dùng vào hệ thống thật. Các vấn đề
đã biết được liệt kê chi tiết trong [`CODE_REVIEW.md`](./CODE_REVIEW.md);
tóm tắt:

- Không phòng chống tấn công **side-channel / timing**.
- Sinh khoá `x` và `k` chỉ dùng `secrets` — đủ ngẫu nhiên về mặt số học,
  nhưng không có tách biệt nhóm con (subgroup hardening) như DSA.
- Chỉ băm `SHA-256`; nếu hash collision sẽ vỡ.
- Không có encoding chuẩn cho chữ ký (DER/ASN.1).

Khi cần chữ ký số trong sản phẩm, dùng **ECDSA / Ed25519** thông qua
thư viện đã được audit (`cryptography`, `libsodium`, …).

## 7. Tài liệu tham khảo

- T. ElGamal, *“A Public Key Cryptosystem and a Signature Scheme Based
  on Discrete Logarithms,”* IEEE Trans. Inf. Theory **31**(4), 1985.
- A. Menezes, P. van Oorschot, S. Vanstone, *Handbook of Applied
  Cryptography*, Chapter 11 (free PDF, [cacr.uwaterloo.ca/hac](https://cacr.uwaterloo.ca/hac/)).
- D. Stinson, *Cryptography: Theory and Practice*, 4th ed., Chapter 7.
