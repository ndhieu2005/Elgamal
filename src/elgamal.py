"""
elgamal.py — Sơ đồ chữ ký số ElGamal (prototype, mục đích học tập)

Tham khảo: T. ElGamal, "A Public-Key Cryptosystem and a Signature Scheme
Based on Discrete Logarithms," IEEE Trans. Inf. Theory, vol. 31, 1985.

Sơ đồ:
    KeyGen:  chọn p nguyên tố lớn, g là căn nguyên thuỷ mod p,
             chọn x ngẫu nhiên trong {1,...,p-2}, tính y = g^x mod p.
             Khoá công khai: (p, g, y); khoá bí mật: x.

    Sign(m): h = H(m) mod (p-1)
             chọn k ngẫu nhiên với gcd(k, p-1) = 1
             r = g^k mod p
             s = (h - x*r) * k^{-1} mod (p-1)   ;  nếu s = 0 thì chọn lại k
             Chữ ký: (r, s)

    Verify(m, (r,s)):  0 < r < p và 0 < s < p-1, và
                        g^h ≡ y^r * r^s  (mod p)
"""

from __future__ import annotations

import hashlib
import secrets
from math import gcd
from typing import Tuple

from Crypto.Util.number import getPrime, isPrime

# --- Kiểu dữ liệu cho rõ ràng -------------------------------------------------
PublicKey = Tuple[int, int, int]   # (p, g, y)
PrivateKey = int                   # x
Signature = Tuple[int, int]        # (r, s)


# --- Sàng bằng các số nguyên tố nhỏ để tăng tốc kiểm tra 2q+1 -----------------
# Lý do: p = 2q+1 là số nguyên tố ⇒ p không chia hết cho bất kỳ số nguyên tố
# nhỏ nào. Sàng trước giúp loại nhanh ~80% ứng viên trước khi gọi Miller–Rabin.
_SMALL_PRIMES = (
    3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67,
    71, 73, 79, 83, 89, 97, 101, 103, 107, 109, 113, 127, 131, 137, 139,
    149, 151, 157, 163, 167, 173, 179, 181, 191, 193, 197, 199, 211, 223,
    227, 229, 233, 239, 241, 251,
)


# --- Tiện ích chung -----------------------------------------------------------
def _random_in_range(low: int, high: int) -> int:
    """Trả về số nguyên ngẫu nhiên trong [low, high] (đóng cả hai đầu).

    Tránh lặp lại pattern `secrets.randbelow(...) + offset` ở nhiều nơi
    (vốn là nguồn lỗi off-by-one phổ biến).
    """
    if low > high:
        raise ValueError(f"low ({low}) > high ({high})")
    return secrets.randbelow(high - low + 1) + low


def generate_safe_prime(bits: int = 1024) -> Tuple[int, int]:
    """Sinh số nguyên tố an toàn p = 2q + 1 với q cũng nguyên tố.

    Vì p = 2q+1, các phần tử trong Z*_p chỉ có cấp 1, 2, q, hoặc 2q.
    Điều này khiến việc tìm căn nguyên thuỷ trở nên đơn giản và đảm bảo
    DLP trong Z*_p khó (không có nhóm con nhỏ để tấn công Pohlig–Hellman).

    Args:
        bits: số bit của p (yêu cầu ≥ 16).

    Returns:
        Cặp (p, q) với p = 2q + 1 và cả hai đều nguyên tố.
    """
    if bits < 16:
        raise ValueError("bits phải ≥ 16")
    while True:
        q = getPrime(bits - 1)
        p = 2 * q + 1
        # Sàng nhanh: nếu p chia hết cho số nguyên tố nhỏ nào → loại
        if any(p % sp == 0 for sp in _SMALL_PRIMES):
            continue
        if isPrime(p):
            return p, q


def find_primitive_root(p: int, q: int) -> int:
    """Tìm căn nguyên thuỷ modulo p khi p = 2q + 1 là safe prime.

    Phần tử g có ord(g) = p − 1 = 2q  ⇔  g² ≢ 1 (mod p)  và  g^q ≢ 1 (mod p).
    Vì p − 1 = 2q chỉ có 2 ước nguyên tố (2 và q), kiểm tra hai luỹ thừa là đủ.
    """
    # Phòng thủ: nếu (p, q) không thoả p = 2q + 1, kết quả không có ý nghĩa
    assert p == 2 * q + 1, "Cần p = 2q + 1 (safe prime)"
    while True:
        g = _random_in_range(2, p - 2)
        if pow(g, 2, p) == 1:                     # ord(g) | 2 → loại
            continue
        if pow(g, q, p) == 1:                     # ord(g) | q → là QR, loại
            continue
        return g                                  # ord(g) = 2q


def _hash_to_int(message: bytes, modulus: int) -> int:
    """Băm SHA-256 rồi rút gọn modulo `modulus` (thường là p − 1).

    Có thêm domain separator b"ElGamal-Sign-v1\\x00" để tránh cross-protocol
    attack nếu sau này dùng SHA-256 cho mục đích khác trong cùng hệ thống.

    Lưu ý giáo dục: SHA-256 cho 256 bit; với p 1024-bit thì hash < p−1 luôn,
    phép mod không thay đổi giá trị. Ta vẫn giữ phép mod để mã đúng cả khi
    p nhỏ hơn 256 bit (ví dụ test với p 512-bit).
    """
    digest = hashlib.sha256(b"ElGamal-Sign-v1\x00" + message).digest()
    return int.from_bytes(digest, "big") % modulus


def keygen(bits: int = 1024) -> Tuple[PublicKey, PrivateKey]:
    """Sinh cặp khoá ElGamal.

    Returns:
        ((p, g, y), x) với y = g^x mod p.
    """
    p, q = generate_safe_prime(bits)
    g = find_primitive_root(p, q)
    x = _random_in_range(1, p - 2)               # khoá bí mật, ∈ [1, p-2]
    y = pow(g, x, p)
    return (p, g, y), x


def sign(message: bytes, public_key: PublicKey,
         private_key: PrivateKey) -> Signature:
    """Ký `message` bằng khoá bí mật.

    Trả về (r, s) thoả s ≠ 0 và 0 < r < p, 0 < s < p − 1.
    """
    p, g, _ = public_key
    x = private_key
    n = p - 1                                     # modulus của số mũ
    h = _hash_to_int(message, n)

    while True:
        # k ∈ [2, p-2] và gcd(k, p-1) = 1 để tồn tại k^{-1} mod (p-1)
        k = _random_in_range(2, p - 2)
        if gcd(k, n) != 1:
            continue
        r = pow(g, k, p)
        if r == 0:                                # phòng thủ: lý thuyết r > 0
            continue
        # pow(k, -1, n) yêu cầu Python ≥ 3.8
        k_inv = pow(k, -1, n)
        s = (k_inv * (h - x * r)) % n
        if s != 0:
            return r, s


def verify(message: bytes, signature: Signature,
           public_key: PublicKey) -> bool:
    """Xác thực chữ ký. Trả về True nếu hợp lệ.

    Điều kiện hợp lệ:
        0 < r < p
        0 < s < p − 1
        g^h ≡ y^r · r^s   (mod p)
    """
    p, g, y = public_key
    r, s = signature

    # Kiểm tra biên — quan trọng để chống forgery dùng r ngoài khoảng
    if not (0 < r < p):
        return False
    if not (0 < s < p - 1):
        return False

    h = _hash_to_int(message, p - 1)
    lhs = pow(g, h, p)
    rhs = (pow(y, r, p) * pow(r, s, p)) % p
    return lhs == rhs
