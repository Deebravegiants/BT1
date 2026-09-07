# [M] Centreon XSS Vulnerability

## Summary
Severity: Medium
Advisory: GHSA-8vh5-j6xj-5953
CVE: CVE-2018-19311
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.0/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-8vh5-j6xj-5953
Type: github-advisory

## Affected
- Packagist: `centreon/centreon` — affected >=18.0.0 <18.10.0

## Details
Centreon 3.4.x (fixed in Centreon 18.10.0) allows XSS via the Service field to the `main.php?p=20201` URI, as demonstrated by the "Monitoring > Status Details > Services" screen.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-19311
- https://github.com/centreon/centreon-archived/pull/6632
- https://documentation.centreon.com/docs/centreon/en/latest/release_notes/centreon-18.10/centreon-18.10.0.html
- http://www.roothc.com.br/1349-2
