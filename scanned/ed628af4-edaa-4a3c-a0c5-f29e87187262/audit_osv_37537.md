# [C] Authenticated SQL Injection in Koha displayby parameter of suggestion.pl

## Summary
Severity: Critical
Advisory: CVE-2026-31844
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-03-11
Source: https://osv.dev/vulnerability/CVE-2026-31844
Type: osv

## Details
An authenticated SQL Injection vulnerability (CWE-89) exists in the Koha staff interface in the /cgi-bin/koha/suggestion/suggestion.pl endpoint due to improper validation of the displayby parameter used by the GetDistinctValues functionality. Successful exploitation may lead to full compromise of the backend database, including disclosure or modification of stored data.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/31xxx/CVE-2026-31844.json
- https://koha-community.gitlab.io/KohaAdvent/2025-12-09-security-all/
- https://koha-community.org/koha-25-11-01-released/
- https://nvd.nist.gov/vuln/detail/CVE-2026-31844
- https://bugs.koha-community.org/bugzilla3/show_bug.cgi?id=41593
