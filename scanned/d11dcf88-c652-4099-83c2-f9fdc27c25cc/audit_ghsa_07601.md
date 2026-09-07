# [M] Subrion CMS vulnerable to cross-site scripting

## Summary
Severity: Medium
Advisory: GHSA-9jjm-mc56-3qxv
CVE: CVE-2025-70958
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2026-02-03
Source: https://github.com/advisories/GHSA-9jjm-mc56-3qxv
Type: github-advisory

## Affected
- Packagist: `intelliants/subrion` — affected >=0

## Details
Multiple reflected Cross-site Scripting (XSS) vulnerabilities in the installation module of Subrion CMS v4.2.1 allow attackers to execute arbitrary Javascript in the context of the user's browser via injecting a crafted payload into the dbuser, dbpwd, and dbname parameters.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-70958
- https://github.com/emirhanyucell/Subrion-CMS-4.2.1/blob/main/subrion-cms-exploit.txt
- https://github.com/intelliants/subrion
