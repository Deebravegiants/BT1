# [M] CVE-2019-12982

## Summary
Severity: Medium
Advisory: CVE-2019-12982
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2019-06-26
Source: https://osv.dev/vulnerability/CVE-2019-12982
Type: osv

## Details
Ming (aka libming) 0.4.8 has a heap buffer overflow and underflow in the decompileCAST function in util/decompile.c in libutil.a. Remote attackers could leverage this vulnerability to cause a denial of service via a crafted SWF file.

## References
- https://github.com/libming/libming/commit/da9d86eab55cbf608d5c916b8b690f5b76bca462
