# [H] misskey.js's export data contains private post data

## Summary
Severity: High
Advisory: GHSA-496g-mmpw-j9x3
CVE: CVE-2025-66402
CWE: CWE-862
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2025-12-15
Source: https://github.com/advisories/GHSA-496g-mmpw-j9x3
Type: github-advisory

## Affected
- npm: `misskey-js` — affected >=13.0.0-beta.16 <2025.12.0

## Details
### Summary

After adding private posts (followers, direct) that you do not have permission to view to your favorites or clips, you can export them to view the contents of the private posts.

### PoC

1. Create an account (X) for testing and an account (Y) for private posts on the same server.
2. Send appropriate content from Y using "Follow"
3. Send appropriate content to any user using "Nominate" from Y
4. Obtain the URLs for the two posts above using Y's account.
5. Query the URLs for the two posts using X and add them to your favorites or clips.
6. Export your favorites or clips using X.
7. Check the exported data.

Note: Verified in v2025.11.1

### Impact

This could allow an attacker to view the contents of private posts.
If you have pinned private posts, this could be a real problem, as the ID of the private post can be obtained by viewing the user page on the original server.

## References
- https://github.com/misskey-dev/misskey/security/advisories/GHSA-496g-mmpw-j9x3
- https://nvd.nist.gov/vuln/detail/CVE-2025-66402
- https://github.com/misskey-dev/misskey/commit/dc77d59f8712d3fe0b73cd4af2035133839cd57b
- https://github.com/misskey-dev/misskey
