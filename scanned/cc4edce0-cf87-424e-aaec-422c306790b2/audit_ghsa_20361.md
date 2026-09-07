# [M] Unpublished, protected files can be published via shortcode

## Summary
Severity: Medium
Advisory: GHSA-v68g-62v9-39w5
CVE: CVE-2022-29858
CWE: CWE-287
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2022-06-29
Source: https://github.com/advisories/GHSA-v68g-62v9-39w5
Type: github-advisory

## Affected
- Packagist: `silverstripe/assets` — affected >=1.0.0 <1.10.1

## Details
Silverstripe silverstripe/assets through 1.10 is vulnerable to improper access control that allows protected images to be published by changing an existing image short code on website content. Draft protected images can be published by changing an existing image shortcode on website content to match the ID of the draft protected image and then publishing the website content.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-29858
- https://github.com/silverstripe/silverstripe-assets/commit/5f6a73b010c01587ffbfb954441f6b7cbb54e767
- https://forum.silverstripe.org/c/releases
- https://github.com/FriendsOfPHP/security-advisories/blob/master/silverstripe/assets/CVE-2022-29858.yaml
- https://huntr.dev/bounties/90e17d95-9f2f-44eb-9f26-49fa13a41d5a
- https://www.silverstripe.org/blog/tag/release
- https://www.silverstripe.org/download/security-releases
- https://www.silverstripe.org/download/security-releases/cve-2022-29858
