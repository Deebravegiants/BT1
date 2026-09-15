# [M] CVE-2022-37770

## Summary
Severity: Medium
Advisory: CVE-2022-37770
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2022-08-18
Source: https://osv.dev/vulnerability/CVE-2022-37770
Type: osv

## Details
libjpeg commit 281daa9 was discovered to contain a segmentation fault via LineMerger::GetNextLowpassLine at linemerger.cpp. This vulnerability allows attackers to cause a Denial of Service (DoS) via a crafted file.

## References
- https://github.com/thorfdbg/libjpeg/issues/79
- https://github.com/thorfdbg/libjpeg/issues/79
- https://github.com/thorfdbg/libjpeg/issues/79
