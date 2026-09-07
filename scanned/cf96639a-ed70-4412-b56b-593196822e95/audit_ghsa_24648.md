# [H] Dolibarr arbitrary commands execution

## Summary
Severity: High
Advisory: GHSA-6j62-m2vv-wc3m
CVE: CVE-2018-10092
CWE: CWE-862
Ecosystem: Packagist
CVSS: CVSS:3.0/AV:N/AC:L/PR:L/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-6j62-m2vv-wc3m
Type: github-advisory

## Affected
- Packagist: `dolibarr/dolibarr` — affected >=0 <7.0.2

## Details
The admin panel in Dolibarr before 7.0.2 might allow remote attackers to execute arbitrary commands by leveraging support for updating the antivirus command and parameters used to scan file uploads.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-10092
- https://github.com/Dolibarr/dolibarr/commit/5d121b2d3ae2a95abebc9dc31e4782cbc61a1f39
- https://github.com/Dolibarr/dolibarr
- https://github.com/Dolibarr/dolibarr/blob/7.0.2/ChangeLog
- https://sysdream.com/news/lab/2018-05-21-cve-2018-10092-dolibarr-admin-panel-authenticated-remote-code-execution-rce-vulnerability
- http://www.openwall.com/lists/oss-security/2018/05/21/2
