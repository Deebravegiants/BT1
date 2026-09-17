# [H] OpenEMR Vulnerable to Authenticated Blind Boolean-Based SQL Injection in new_search_popup.php

## Summary
Severity: High
Advisory: CVE-2026-29187
Aliases: GHSA-2r7h-xm8v-m872
CVSS: 8.1 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:N)
Published: 2026-03-25
Source: https://osv.dev/vulnerability/CVE-2026-29187
Type: osv

## Details
OpenEMR is a free and open source electronic health records and medical practice management application. Prior to version 8.0.0.3, a Blind SQL Injection vulnerability exists in the Patient Search functionality (/interface/new/new_search_popup.php). The vulnerability allows an authenticated attacker to execute arbitrary SQL commands by manipulating the HTTP parameter keys rather than the values. Version 8.0.0.3 contains a patch.

## References
- https://github.com/openemr/openemr/releases/tag/v8_0_0_3
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/29xxx/CVE-2026-29187.json
- https://github.com/openemr/openemr/security/advisories/GHSA-2r7h-xm8v-m872
- https://nvd.nist.gov/vuln/detail/CVE-2026-29187
- https://github.com/openemr/openemr/commit/c61887aa7c83e83b3282db05246f1c00de3aa21d
