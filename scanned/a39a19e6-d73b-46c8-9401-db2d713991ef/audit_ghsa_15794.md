# [H] EGroupware mishandles an ORDER BY clause

## Summary
Severity: High
Advisory: GHSA-phg7-8mm9-gj88
CVE: CVE-2024-40614
CWE: CWE-89
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2024-07-07
Source: https://github.com/advisories/GHSA-phg7-8mm9-gj88
Type: github-advisory

## Affected
- Packagist: `egroupware/egroupware` — affected >=0 <23.1.20240624

## Details
EGroupware before 23.1.20240624 mishandles an ORDER BY clause. This leads to json.php menuaction=EGroupware\Api\Etemplate\Widget\Nextmatch::ajax_get_rows sort.id SQL injection by authenticated users for Address Book or InfoLog sorting.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-40614
- https://github.com/EGroupware/egroupware/commit/553829d30cc2ccdc0e5a8c5a0e16fa03a3399a3f
- https://github.com/EGroupware/egroupware
- https://github.com/EGroupware/egroupware/compare/23.1.20240430...23.1.20240624
- https://github.com/EGroupware/egroupware/releases/tag/23.1.20240624
- https://help.egroupware.org/t/egroupware-maintenance-security-release-23-1-20240624/78438
- https://syss.de
- https://www.syss.de/fileadmin/dokumente/Publikationen/Advisories/SYSS-2024-047.txt
- https://www.syss.de/pentest-blog/sql-injection-schwachstelle-in-egroupware-syss-2024-047
