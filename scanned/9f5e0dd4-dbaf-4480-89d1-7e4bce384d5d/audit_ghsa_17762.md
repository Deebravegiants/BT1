# [M] Silverstripe Framework has a XSS via insert media remote file oembed

## Summary
Severity: Medium
Advisory: GHSA-7cmp-cgg8-4c82
CVE: CVE-2024-47605
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2025-01-14
Source: https://github.com/advisories/GHSA-7cmp-cgg8-4c82
Type: github-advisory

## Affected
- Packagist: `silverstripe/framework` — affected >=0 <5.3.8

## Details
### Impact

When using the "insert media" functionality, the linked oEmbed JSON includes an HTML attribute which will replace the embed shortcode. The HTML is not sanitized before replacing the shortcode, allowing a script payload to be executed on both the CMS and the front-end of the website.

## References

- https://www.silverstripe.org/download/security-releases/cve-2024-47605

## Reported by

James Nicoll from [Fujitsu Cyber Security Services](https://www.fujitsu.com/nz/services/security/)

## References
- https://github.com/silverstripe/silverstripe-asset-admin/security/advisories/GHSA-7cmp-cgg8-4c82
- https://nvd.nist.gov/vuln/detail/CVE-2024-47605
- https://github.com/silverstripe/silverstripe-framework/commit/09b5052c86932f273e0d733428c9aade70ff2a4a
- https://github.com/FriendsOfPHP/security-advisories/blob/master/silverstripe/framework/CVE-2024-47605.yaml
- https://github.com/silverstripe/silverstripe-framework
- https://www.silverstripe.org/download/security-releases/cve-2024-47605
