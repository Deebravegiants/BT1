# [H] CVE-2022-0306

## Summary
Severity: High
Advisory: CVE-2022-0306
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2022-02-12
Source: https://osv.dev/vulnerability/CVE-2022-0306
Type: osv

## Details
Heap buffer overflow in PDFium in Google Chrome prior to 97.0.4692.99 allowed a remote attacker to potentially exploit heap corruption via a crafted HTML page.

## References
- http://packetstormsecurity.com/files/166367/Chrome-chrome_pdf-PDFiumEngine-RequestThumbnail-Heap-Buffer-Overflow.html
- https://chromereleases.googleblog.com/2022/01/stable-channel-update-for-desktop_19.html
- https://crbug.com/1283198
