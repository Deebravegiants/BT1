# [M] Pixelfed may allow unauthorized actor to view private posts and private users

## Summary
Severity: Medium
Advisory: GHSA-7287-grhx-542x
CVE: CVE-2025-30741
CWE: CWE-863
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2025-03-25
Source: https://github.com/advisories/GHSA-7287-grhx-542x
Type: github-advisory

## Affected
- Packagist: `pixelfed/pixelfed` — affected >=0 <0.12.5

## Details
Pixelfed before 0.12.5 allows anyone to follow private accounts and see private posts on other Fediverse servers. This affects users elsewhere in the Fediverse, if they otherwise have any followers from a Pixelfed instance.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-30741
- https://fokus.cool/2025/03/25/pixelfed-vulnerability.html
- https://github.com/pixelfed/pixelfed
- https://github.com/pixelfed/pixelfed/releases/tag/v0.12.5
- https://mastodon.social/@pixelfed/114215925957179498
- https://news.ycombinator.com/item?id=43474425
