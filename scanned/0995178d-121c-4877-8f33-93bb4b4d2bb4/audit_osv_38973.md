# [H] media: verisilicon: AV1: Fix tile info buffer size

## Summary
Severity: High
Advisory: CVE-2026-43222
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-05-06
Source: https://osv.dev/vulnerability/CVE-2026-43222
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.5.0 <6.6.128, >=6.7.0 <6.12.75, >=6.13.0 <6.18.16, >=6.19.0 <6.19.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

media: verisilicon: AV1: Fix tile info buffer size

Each tile info is composed of: row_sb, col_sb, start_pos
and end_pos (4 bytes each). So the total required memory
is AV1_MAX_TILES * 16 bytes.
Use the correct #define to allocate the buffer and avoid
writing tile info in non-allocated memory.

## References
- https://git.kernel.org/stable/c/34f36f9c6114af781a5a4f7a7c99334c85b73fc7
- https://git.kernel.org/stable/c/74abfadd7ef5ac9f3a6111d550cc651d1457c641
- https://git.kernel.org/stable/c/a505ca2db89ad92a8d8d27fa68ebafb12e04a679
- https://git.kernel.org/stable/c/a5b1ddbe31f49b4da78642157589970e9b60a231
- https://git.kernel.org/stable/c/f122f2b3ce9dbde60bf7ab0b180fe4a01f9d9bc4
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/43xxx/CVE-2026-43222.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-43222
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
