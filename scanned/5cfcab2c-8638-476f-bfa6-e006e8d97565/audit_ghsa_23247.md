# [M] Dolibarr Cross-site Scripting in a User Note section

## Summary
Severity: Medium
Advisory: GHSA-m44p-cfwj-wwr6
CVE: CVE-2019-16686
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-m44p-cfwj-wwr6
Type: github-advisory

## Affected
- Packagist: `dolibarr/dolibarr` — affected 9.0.5

## Details
Dolibarr 9.0.5 has stored XSS in a User Note section to note.php. A user with no privileges can inject script to attack the admin.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-16686
- https://github.com/Dolibarr/dolibarr
- http://verneet.com/cve-2019-16686
