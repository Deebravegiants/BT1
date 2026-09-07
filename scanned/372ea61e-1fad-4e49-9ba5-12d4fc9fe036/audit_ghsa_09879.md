# [H] Dolibarr user with permission to edit PHP content can bypass filtering to restrict dangerous PHP functions

## Summary
Severity: High
Advisory: GHSA-j2g9-rprv-hrhc
CVE: CVE-2026-31019
CWE: CWE-78
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-04-21
Source: https://github.com/advisories/GHSA-j2g9-rprv-hrhc
Type: github-advisory

## Affected
- Packagist: `dolibarr/dolibarr` — affected >=0

## Details
In the Website module of Dolibarr ERP & CRM 22.0.4 and below, the application uses blacklist-based filtering to restrict dangerous PHP functions related to system command execution. An authenticated user with permission to edit PHP content can bypass this filtering, resulting in full remote code execution with the ability to execute arbitrary operating system commands on the server.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-31019
- https://github.com/Dolibarr/dolibarr
- https://github.com/PhDg1410/CVE/blob/main/CVE-2026-31019/README.md
- http://dolibarr.com
