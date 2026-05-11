# Lược đồ chữ ký số ElGamal

Báo cáo Đồ Án Tốt Nghiệp về **Lược đồ chữ ký số ElGamal và ứng dụng xác thực tài liệu số**.

Trường Đại học Bách Khoa Hà Nội — Khoa Toán - Tin (SoICT).

---

## Quick Start

```bash
cd report/Do_an_LaTEX_Based_by_SoICT
latexmk -pdf -bibtex DoAn.tex
```

Yêu cầu: TeX Live 2023+ hoặc MiKTeX 25+ (bản full). Xem [Prerequisites](#prerequisites) bên dưới.

---

## Cấu trúc thư mục

```
Elgamal/
├── report/
│   └── Do_an_LaTEX_Based_by_SoICT/
│       ├── DoAn.tex                         # File LaTeX chính
│       ├── Bia.tex                          # Trang bìa (subfile)
│       ├── Danh_sach_tai_lieu_tham_khao.bib # Tài liệu tham khảo
│       ├── Tu_viet_tat.tex                  # Từ viết tắt / glossary
│       ├── lstlisting.tex                   # Cấu hình listings package
│       ├── .latexmkrc                       # Config cho latexmk
│       ├── Makefile                         # Build automation
│       ├── Chuong/                          # Các chương (subfiles)
│       └── Hinhve/                          # Hình ảnh
├── src/                                     # Mã nguồn cài đặt
├── experiments/                             # Thí nghiệm / dữ liệu
└── slides/                                  # Slide thuyết trình
```

---

## Prerequisites

Mọi lệnh compile đều phải chạy từ bên trong thư mục:
```
report/Do_an_LaTEX_Based_by_SoICT/
```

### TeX Distribution

| Hệ điều hành | Distribution khuyến nghị | Tải về |
|--------------|--------------------------|--------|
| Windows      | MiKTeX 25.4+             | https://miktex.org/download |
| Linux        | TeX Live 2023+           | `sudo apt install texlive-full` |
| macOS        | MacTeX 2023+             | https://www.tug.org/mactex/ |

> **Quan trọng:** Cài bản **full** (không phải "basic" hay "small"). Document dùng hơn 30 packages.
> MiKTeX có thể tự tải packages còn thiếu khi compile lần đầu nếu có kết nối mạng.

### Công cụ cần có trong PATH

| Công cụ | Mục đích |
|---------|---------|
| `pdflatex` | Compiler chính — **dùng cái này, không dùng xelatex/lualatex** |
| `biber` | Backend xử lý bibliography (biblatex) |
| `latexmk` | Tự động hóa multi-pass build |
| `makeglossaries` | Xử lý glossary (hiện đang tắt, dùng sau) |

Kiểm tra cài đặt:
```bash
pdflatex --version
biber --version
latexmk --version
```

---

## Hướng dẫn Compile

### Cách A — latexmk (Khuyến nghị)

```bash
# Chạy từ report/Do_an_LaTEX_Based_by_SoICT/
latexmk -pdf -bibtex DoAn.tex
```

latexmk tự động xử lý tất cả các pass (pdflatex → biber → pdflatex → pdflatex) và chỉ chạy lại những gì thay đổi.

Xóa file tạm (giữ PDF):
```bash
latexmk -c DoAn.tex
```

Xóa tất cả kể cả PDF:
```bash
latexmk -C DoAn.tex
```

### Cách B — Makefile

```bash
# Chạy từ report/Do_an_LaTEX_Based_by_SoICT/
make          # compile (mặc định)
make clean    # xóa file tạm, giữ PDF
make cleanall # xóa tất cả kể cả PDF
make watch    # compile liên tục khi file thay đổi
```

Windows cần GNU Make: `choco install make` (qua Chocolatey).

### Cách C — Thủ công (từng bước)

```bash
# Chạy từ report/Do_an_LaTEX_Based_by_SoICT/
pdflatex DoAn.tex        # Pass 1: tạo .aux và .bcf
biber DoAn               # Xử lý bibliography
makeglossaries DoAn      # Xử lý glossary (nếu cần)
pdflatex DoAn.tex        # Pass 2: nhúng bibliography
pdflatex DoAn.tex        # Pass 3: hoàn thiện cross-reference, TOC
```

Output: `DoAn.pdf`

### Cách D — VS Code với LaTeX Workshop

1. Cài extension [LaTeX Workshop](https://marketplace.visualstudio.com/items?itemName=James-Yu.latex-workshop).
2. Mở `DoAn.tex`.
3. Thêm vào `.vscode/settings.json` của workspace:

```json
{
  "latex-workshop.latex.tools": [
    {
      "name": "pdflatex",
      "command": "pdflatex",
      "args": ["-synctex=1", "-interaction=nonstopmode", "-file-line-error", "%DOC%"]
    },
    { "name": "biber", "command": "biber", "args": ["%DOCFILE%"] }
  ],
  "latex-workshop.latex.recipes": [
    {
      "name": "pdflatex + biber + pdflatex×2",
      "tools": ["pdflatex", "biber", "pdflatex", "pdflatex"]
    }
  ],
  "latex-workshop.latex.outDir": "%DIR%"
}
```

---

## Lưu ý kỹ thuật

| Vấn đề | Chi tiết |
|--------|---------|
| **Compiler** | Chỉ dùng **pdflatex** — không dùng xelatex hay lualatex |
| **Bibliography** | Backend là **biber**, không phải bibtex truyền thống |
| **Thư mục ảnh** | Ảnh nằm trong `Hinhve/`, không phải `figures/` |
| **Subfiles** | `Bia.tex` có thể compile độc lập ra `Bia.pdf` (file tạm, không track git) |
| **Glossary** | `\printnoidxglossaries` đang bị comment out — bước `makeglossaries` là tùy chọn |

---

## Packages sử dụng

Tất cả đều có sẵn trong TeX Live full / MiKTeX full:

`scrextend`, `geometry`, `fancyhdr`, `pdflscape`, `setspace`, `afterpage`,
`graphicx`, `array`, `multirow`, `subcaption`, `float`, `caption`, `capt-of`,
`amsmath`, `amssymb`, `amsthm`, `algorithm2e`, `vietnam`, `times`, `indentfirst`,
`titlesec`, `titletoc`, `biblatex` (biber), `appendix`, `listings`, `xurl`,
`glossaries`, `glossary-superragged`, `fancybox`, `eso-pic`, `subfiles`,
`enumitem`, `hyperref`, `hypcap`, `outlines`

---

## Đóng góp

1. Fork repo này trên GitHub.
2. Clone fork của bạn: `git clone https://github.com/YOUR_USERNAME/Elgamal.git`
3. Compile thử để xác nhận baseline hoạt động (theo hướng dẫn trên).
4. Làm việc trên branch: `git checkout -b feature/ten-chuong`
5. Tạo pull request.
