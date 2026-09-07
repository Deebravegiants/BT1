# [M] Dolibarr Cross-site Scripting via outgoing email setup feature

## Summary
Severity: Medium
Advisory: GHSA-r4gf-ggp5-25g5
CVE: CVE-2019-17577
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-r4gf-ggp5-25g5
Type: github-advisory

## Affected
- Packagist: `dolibarr/dolibarr` — affected 10.0.2

## Details
An issue was discovered in Dolibarr 10.0.2. It has XSS via the "outgoing email setup" feature in the admin/mails.php?action=edit URI via the "Email used for error returns emails (fields 'Errors-To' in emails sent)" field.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-17577
- https://github.com/Dolibarr/dolibarr
- https://mycvee.blogspot.com/p/cve-2019-17576.html
