# [M] Browsershot Local File Inclusion

## Summary
Severity: Medium
Advisory: GHSA-g2r4-phv7-5fgv
CVE: CVE-2024-21544
CWE: CWE-20
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:N/A:N (CVSS_V3)
Published: 2024-12-13
Source: https://github.com/advisories/GHSA-g2r4-phv7-5fgv
Type: github-advisory

## Affected
- Packagist: `spatie/browsershot` — affected >=0 <5.0.1

## Details
Versions of the package spatie/browsershot before 5.0.1 are vulnerable to Improper Input Validation due to improper URL validation through the setUrl method.
An attacker can exploit this vulnerability by using leading whitespace (%20) before the file:// protocol, resulting in Local File Inclusion, which allows the attacker to read sensitive files on the server.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-21544
- https://github.com/spatie/browsershot/commit/fae8396641b961f62bd756920b14f01a4391296e
- https://github.com/spatie/browsershot
- https://github.com/spatie/browsershot/blob/1e212b596c104138550ed4ef1b9977d8df570c67/src/Browsershot.php%23L258-L269
- https://security.snyk.io/vuln/SNYK-PHP-SPATIEBROWSERSHOT-8496745
