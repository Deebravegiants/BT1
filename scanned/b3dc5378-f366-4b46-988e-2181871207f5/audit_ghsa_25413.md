# [M] Dolibarr CRM allows Privilege Escalation

## Summary
Severity: Medium
Advisory: GHSA-25h3-mw3p-w8r7
CVE: CVE-2020-14201
CWE: CWE-269
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-25h3-mw3p-w8r7
Type: github-advisory

## Affected
- Packagist: `dolibarr/dolibarr` — affected >=0 <11.0.5

## Details
Dolibarr CRM before 11.0.5 allows privilege escalation. This could allow remote authenticated attackers to upload arbitrary files via societe/document.php in which "disabled" is changed to "enabled" in the HTML source code.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-14201
- https://github.com/Dolibarr/dolibarr
- https://github.com/Dolibarr/dolibarr/blob/e76641c491e4105e9cb1ded6149771c621d822b5/ChangeLog#L2933
- https://www.wizlynxgroup.com/security-research-advisories/vuln/WLX-2020-011
