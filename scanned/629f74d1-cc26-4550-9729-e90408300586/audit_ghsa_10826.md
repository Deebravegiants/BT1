# [M] Yoast Duplicate Post has an Authenticated (Contributor+) Missing Authorization to Arbitrary Post Duplication and Overwrite

## Summary
Severity: Medium
Advisory: GHSA-g9w4-m5fx-x3wv
CVE: CVE-2026-1217
CWE: CWE-862
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2026-03-18
Source: https://github.com/advisories/GHSA-g9w4-m5fx-x3wv
Type: github-advisory

## Affected
- Packagist: `yoast/duplicate-post` — affected >=0 <4.6

## Details
The Yoast Duplicate Post plugin for WordPress is vulnerable to unauthorized modification of data due to a missing capability check on the clone_bulk_action_handler() and republish_request() functions in all versions up to, and including, 4.5. This makes it possible for authenticated attackers, with Contributor-level access and above, to duplicate any post on the site including private, draft, and trashed posts they shouldn't have access to. Additionally, attackers with Author-level access and above can use the Rewrite & Republish feature to overwrite any published post with their own content.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-1217
- https://github.com/Yoast-dist/duplicate-post
- https://plugins.trac.wordpress.org/browser/duplicate-post/tags/4.5/src/handlers/bulk-handler.php#L115
- https://plugins.trac.wordpress.org/browser/duplicate-post/tags/4.5/src/post-republisher.php#L128
- https://www.wordfence.com/threat-intel/vulnerabilities/id/05f175e6-08a9-4199-948c-5bd8b3caaa39?source=cve
