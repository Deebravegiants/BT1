# [C] editorconfig-core-c has incomplete fix for CVE-2023-0341

## Summary
Severity: Critical
Advisory: CVE-2026-40489
Aliases: GHSA-97xg-vrcq-254h
CVSS: 9.0 (CVSS:4.0/AV:L/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-04-18
Source: https://osv.dev/vulnerability/CVE-2026-40489
Type: osv

## Details
editorconfig-core-c  is an EditorConfig core library for use by plugins supporting EditorConfig parsing. Versions up to and including 0.12.10 have a stack-based buffer overflow in ec_glob() that allows an attacker to crash any application using libeditorconfig by providing a specially crafted directory structure and .editorconfig file. This is an incomplete fix for CVE-2023-0341. The pcre_str buffer was protected in 0.12.6 but the adjacent l_pattern[8194] stack buffer received no equivalent protection. On Ubuntu 24.04, FORTIFY_SOURCE converts the overflow to SIGABRT (DoS). Version 0.12.11 contains an updated fix.

## References
- https://github.com/editorconfig/editorconfig-core-c/releases/tag/v0.12.11
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/40xxx/CVE-2026-40489.json
- https://github.com/editorconfig/editorconfig-core-c/security/advisories/GHSA-97xg-vrcq-254h
- https://nvd.nist.gov/vuln/detail/CVE-2026-40489
- https://github.com/editorconfig/editorconfig-core-c/commit/5159be88ad50641d9843289adda791ba300421ff
