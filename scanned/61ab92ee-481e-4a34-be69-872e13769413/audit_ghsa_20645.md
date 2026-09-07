# [M] Insufficient Session Expiration in snipe/snipe-it 

## Summary
Severity: Medium
Advisory: GHSA-cmxc-9ghj-jp87
CVE: CVE-2022-2997
CWE: CWE-384
Ecosystem: Packagist
CVSS: CVSS:3.0/AV:N/AC:L/PR:L/UI:R/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2022-08-26
Source: https://github.com/advisories/GHSA-cmxc-9ghj-jp87
Type: github-advisory

## Affected
- Packagist: `snipe/snipe-it` — affected >=0 <6.0.10

## Details
Session Fixation in GitHub repository snipe/snipe-it prior to version 6.0.10. The session is not invalidated after a password change.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-2997
- https://github.com/snipe/snipe-it/commit/6fde72a69335c80079363b7d26aa94e7f67400e1
- https://github.com/snipe/snipe-it
- https://huntr.dev/bounties/c09bf21b-50d2-49f0-8c92-49f6b3c358d8
