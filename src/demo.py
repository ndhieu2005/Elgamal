"""
demo.py — Chạy thử prototype ElGamal với p = 1024-bit.

Cách chạy:
    python demo.py
    python demo.py --bits 512        # chạy nhanh để kiểm tra
"""

import argparse
import time

from elgamal import keygen, sign, verify


def _short(n: int, head: int = 24, tail: int = 12) -> str:
    """In số lớn rút gọn, không làm tràn terminal."""
    s = str(n)
    if len(s) <= head + tail + 5:
        return s
    return f"{s[:head]} … {s[-tail:]}  ({len(s)} chữ số)"


def main() -> None:
    parser = argparse.ArgumentParser(description="ElGamal prototype demo")
    parser.add_argument("--bits", type=int, default=1024,
                        help="kích thước p (mặc định 1024)")
    parser.add_argument("--message", type=str,
                        default="Day la van ban mau de ky bang ElGamal. "
                                "Trung — HUST, Toan-Tin.",
                        help="văn bản cần ký")
    args = parser.parse_args()

    print("=" * 64)
    print(f" ElGamal Digital Signature — Prototype Demo  (p = {args.bits}-bit)")
    print("=" * 64)

    # 1) Sinh khoá
    print("\n[1] Sinh cặp khoá …")
    t0 = time.time()
    (p, g, y), x = keygen(bits=args.bits)
    print(f"    Hoàn tất sau {time.time() - t0:.2f}s "
          f"(p có {p.bit_length()} bit)")
    print(f"    p = {_short(p)}")
    print(f"    g = {_short(g)}")
    print(f"    y = g^x mod p = {_short(y)}")
    print(f"    x (bí mật) = {_short(x)}")

    # 2) Ký văn bản
    message = args.message.encode("utf-8")
    print(f"\n[2] Văn bản cần ký: {args.message!r}")
    print("    Đang ký …")
    t0 = time.time()
    r, s = sign(message, (p, g, y), x)
    print(f"    Hoàn tất sau {(time.time() - t0)*1000:.1f} ms")
    print(f"    r = {_short(r)}")
    print(f"    s = {_short(s)}")

    # 3) Xác thực với văn bản gốc
    print("\n[3] Xác thực chữ ký với văn bản gốc …")
    t0 = time.time()
    ok = verify(message, (r, s), (p, g, y))
    print(f"    Hoàn tất sau {(time.time() - t0)*1000:.1f} ms")
    print(f"    Kết quả: {'HỢP LỆ ✓' if ok else 'KHÔNG HỢP LỆ ✗'}")
    assert ok, "Chữ ký phải hợp lệ với văn bản gốc!"

    # 4) Test phát hiện giả mạo
    print("\n[4] Xác thực chữ ký trên văn bản đã bị sửa …")
    tampered = b"Day la van ban gia mao."
    ok2 = verify(tampered, (r, s), (p, g, y))
    print(f"    Kết quả: {'HỢP LỆ ✓' if ok2 else 'KHÔNG HỢP LỆ ✗  (đúng)'}")
    assert not ok2, "Chữ ký KHÔNG được hợp lệ với văn bản bị sửa!"

    # 5) Test phát hiện chữ ký bị sửa
    print("\n[5] Xác thực chữ ký bị thay đổi (s + 1) …")
    ok3 = verify(message, (r, s + 1), (p, g, y))
    print(f"    Kết quả: {'HỢP LỆ ✓' if ok3 else 'KHÔNG HỢP LỆ ✗  (đúng)'}")
    assert not ok3

    print("\n" + "=" * 64)
    print(" Tất cả kiểm tra đã PASS.")
    print("=" * 64)


if __name__ == "__main__":
    main()
