# [M] Drupal Open Social allows Functionality Misuse

## Summary
Severity: Medium
Advisory: GHSA-63wg-87qv-rw4r
CVE: CVE-2024-13274
CWE: CWE-799
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L (CVSS_V3)
Published: 2025-01-09
Source: https://github.com/advisories/GHSA-63wg-87qv-rw4r
Type: github-advisory

## Affected
- Packagist: `goalgorilla/open_social` — affected >=0 <12.3.8
- Packagist: `goalgorilla/open_social` — affected >=12.4.0 <12.4.5
- Packagist: `goalgorilla/open_social` — affected >=13.0.0-alpha1 <13.0.0-alpha11

## Details
The distribution didn't validate the flood control limits on the password reset form correctly resulting in a potential attacker flooding the password reset which could result in a Denial of Service. Fortunately the message does not disclose any information to the attacker.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-13274
- https://github.com/goalgorilla/open_social
- https://www.drupal.org/sa-contrib-2024-038
