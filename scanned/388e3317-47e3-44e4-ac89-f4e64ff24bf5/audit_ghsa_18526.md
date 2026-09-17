# [H] SQLitePCLRaw.lib.e_sqlite3 has a vulnerable dependency on SQLite

## Summary
Severity: High
Advisory: GHSA-2m69-gcr7-jv3q
CVE: CVE-2025-6965
CWE: CWE-197
Ecosystem: NuGet
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2025-07-15
Source: https://github.com/advisories/GHSA-2m69-gcr7-jv3q
Type: github-advisory

## Affected
- NuGet: `SQLitePCLRaw.lib.e_sqlite3` — affected >=0
- NuGet: `SQLitePCLRaw.lib.e_sqlite3.android` — affected >=0
- NuGet: `SQLitePCLRaw.lib.e_sqlite3.ios` — affected >=0

## Details
There exists a vulnerability in SQLite versions before 3.50.2 where the number of aggregate terms could exceed the number of columns available. This could lead to a memory corruption issue. We recommend upgrading to version 3.50.2 or above.

## References
- https://github.com/google/security-research/security/advisories/GHSA-qj7j-3jp8-8ccv
- https://nvd.nist.gov/vuln/detail/CVE-2025-6965
- https://github.com/github/advisory-database/pull/7675
- https://cert-portal.siemens.com/productcert/html/ssa-225816.html
- https://cert-portal.siemens.com/productcert/html/ssa-485750.html
- https://github.com/ericsink/SQLitePCL.raw
- https://www.sqlite.org/src/info/5508b56fd24016c13981ec280ecdd833007c9d8dd595edb295b984c2b487b5c8
- http://seclists.org/fulldisclosure/2025/Sep/49
- http://seclists.org/fulldisclosure/2025/Sep/53
- http://seclists.org/fulldisclosure/2025/Sep/56
- http://seclists.org/fulldisclosure/2025/Sep/57
- http://seclists.org/fulldisclosure/2025/Sep/58
- http://www.openwall.com/lists/oss-security/2025/09/06/1
