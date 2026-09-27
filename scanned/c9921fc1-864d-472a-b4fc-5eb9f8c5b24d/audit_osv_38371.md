# [M] Scoold has an Authenticated Arbitrary Question Overwrite via Client-Controlled postId in POST /questions/ask

## Summary
Severity: Medium
Advisory: CVE-2026-39354
Aliases: GHSA-768r-cv9p-wrcm
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:N)
Published: 2026-04-07
Source: https://osv.dev/vulnerability/CVE-2026-39354
Type: osv

## Details
Scoold is a Q&A and a knowledge sharing platform for teams. Prior to 1.66.2, an authenticated authorization flaw in Scoold allows any logged-in, low-privilege user to overwrite another user's existing question by supplying that question's public ID as the postId parameter to POST /questions/ask. Because question IDs are exposed in normal question URLs, a low-privilege attacker can take a victim question ID from a public page and cause attacker-controlled content to be stored under that existing question object. This causes direct integrity loss of user-generated content and corrupts the integrity of the existing discussion thread. This vulnerability is fixed in 1.66.2.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/39xxx/CVE-2026-39354.json
- https://github.com/Erudika/scoold/security/advisories/GHSA-768r-cv9p-wrcm
- https://nvd.nist.gov/vuln/detail/CVE-2026-39354
