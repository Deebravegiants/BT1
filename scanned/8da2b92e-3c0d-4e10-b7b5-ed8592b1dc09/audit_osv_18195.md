# [M] CVE-2020-24890

## Summary
Severity: Medium
Advisory: CVE-2020-24890
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2020-09-16
Source: https://osv.dev/vulnerability/CVE-2020-24890
Type: osv

## Details
libraw 20.0 has a null pointer dereference vulnerability in parse_tiff_ifd in src/metadata/tiff.cpp, which may result in context-dependent arbitrary code execution. Note: this vulnerability occurs only if you compile the software in a certain way

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/EWHUZCRMGOC3QS6C65KWBM6ZJM25V6HI/
- https://security.gentoo.org/glsa/202010-05
- https://github.com/LibRaw/LibRaw/issues/335
