# [M] Dolibarr stored Cross-site Scripting in an Email Template section

## Summary
Severity: Medium
Advisory: GHSA-9h46-g4c9-7976
CVE: CVE-2019-16688
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-9h46-g4c9-7976
Type: github-advisory

## Affected
- Packagist: `dolibarr/dolibarr` — affected 9.0.5

## Details
Dolibarr 9.0.5 has stored XSS in an Email Template section to mails_templates.php. A user with no privileges can inject script to attack the admin. (This stored XSS can affect all types of user privilege from Admin to users with no permissions.)

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-16688
- https://github.com/Dolibarr/dolibarr
- http://verneet.com/cve-2019-16688
