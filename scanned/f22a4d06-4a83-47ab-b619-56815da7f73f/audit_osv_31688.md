# [H] ClipBucket V5 Avatar URL Path Traversal to Arbitrary File Delete

## Summary
Severity: High
Advisory: CVE-2025-21622
Aliases: GHSA-5qpx-23rw-36gg
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-01-07
Source: https://osv.dev/vulnerability/CVE-2025-21622
Type: osv

## Details
ClipBucket V5 provides open source video hosting with PHP. During the user avatar upload workflow, a user can choose to upload and change their avatar at any time. During deletion, ClipBucket checks for the avatar_url as a filepath within the avatars subdirectory. If the URL path exists within the avatars directory, ClipBucket will delete it. There is no check for path traversal sequences in the provided user input (stored in the DB as avatar_url) therefore the final $file variable could be tainted with path traversal sequences. This leads to file deletion outside of the intended scope of the avatars folder. This vulnerability is fixed in 5.5.1 - 237.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/21xxx/CVE-2025-21622.json
- https://github.com/MacWarrior/clipbucket-v5/security/advisories/GHSA-5qpx-23rw-36gg
- https://nvd.nist.gov/vuln/detail/CVE-2025-21622
- https://github.com/MacWarrior/clipbucket-v5/commit/22329c4675e82c7c95e74024ba247f837ac9e00b
