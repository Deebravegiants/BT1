# [M] QloApps 1.7.0 Weak Password Hashing via MD5 in Tools.php

## Summary
Severity: Medium
Advisory: CVE-2026-25861
CVSS: 6.0 (CVSS:4.0/AV:N/AC:H/AT:N/PR:N/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N)
Published: 2026-06-02
Source: https://osv.dev/vulnerability/CVE-2026-25861
Type: osv

## Details
QloApps through 1.7.0, fixed in commit 64e9722, contains a weak cryptographic algorithm vulnerability that allows attackers to compromise user credentials by exploiting the use of MD5 for password hashing in the Tools::encrypt() function within classes/Tools.php, which concatenates a static cookie key with the supplied password. Attackers can perform offline brute-force attacks against the MD5 hashes, with the risk compounded by auto-generated 8-character passwords assigned during guest-to-customer account conversion in classes/Customer.php, making credential recovery trivial.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/25xxx/CVE-2026-25861.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-25861
- https://www.vulncheck.com/advisories/qloapps-weak-password-hashing-via-md5-in-tools-php
- https://github.com/Qloapps/QloApps/pull/1689
- https://github.com/Qloapps/QloApps/commit/64e9722e7e6a8fda77dd53964d988fb6b5c3d174
- https://github.com/Qloapps/QloApps
