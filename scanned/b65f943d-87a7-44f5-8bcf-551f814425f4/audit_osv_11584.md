# [M] CVE-2017-8845

## Summary
Severity: Medium
Advisory: CVE-2017-8845
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-05-08
Source: https://osv.dev/vulnerability/CVE-2017-8845
Type: osv

## Details
The lzo1x_decompress function in lzo1x_d.ch in LZO 2.08, as used in lrzip 0.631, allows remote attackers to cause a denial of service (invalid memory read and application crash) via a crafted archive.

## References
- https://blogs.gentoo.org/ago/2017/05/07/lrzip-invalid-memory-read-in-lzo_decompress_buf-stream-c/
- https://security.gentoo.org/glsa/202005-01
- https://github.com/ckolivas/lrzip/issues/68
