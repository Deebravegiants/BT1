# [M] CVE-2018-11379

## Summary
Severity: Medium
Advisory: CVE-2018-11379
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2018-05-22
Source: https://osv.dev/vulnerability/CVE-2018-11379
Type: osv

## Details
The get_debug_info() function in radare2 2.5.0 allows remote attackers to cause a denial of service (heap-based out-of-bounds read and application crash) via a crafted PE file.

## References
- https://github.com/radare/radare2/issues/9926
- https://github.com/radare/radare2/commit/4e1cf0d3e6f6fe2552a269def0af1cd2403e266c
