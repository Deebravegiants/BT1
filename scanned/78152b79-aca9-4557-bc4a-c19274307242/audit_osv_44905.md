# [M] rclone local: crafted Range request against a translated symlink panics (DoS)

## Summary
Severity: Medium
Advisory: CVE-2026-88015
Aliases: GHSA-p6m2-r3w9-mpxw
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L)
Published: 2026-09-10
Source: https://osv.dev/vulnerability/CVE-2026-88015
Type: osv

## Details
rclone is a command-line program to sync files and directories to and from different cloud storage providers. Prior to 1.75.1, backend/local with --links or links=true exposes symlink targets as .rclonelink objects, and fs.RangeOption.Decode can pass an unchecked positive Range start through Object.Open and openTranslatedLink. The function slices the target string as linkdst[offset:], so a Range start larger than the target length causes a deterministic slice-bounds panic when lib/http/serve exposes the object through HTTP or WebDAV. Go net/http normally recovers the panic per connection, causing request-level denial of service rather than terminating the entire process. This issue is fixed in version 1.75.1.

## References
- https://github.com/rclone/rclone/releases/tag/v1.75.1
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/88xxx/CVE-2026-88015.json
- https://github.com/rclone/rclone/security/advisories/GHSA-p6m2-r3w9-mpxw
- https://nvd.nist.gov/vuln/detail/CVE-2026-88015
- https://github.com/rclone/rclone/commit/28bf49d66f94acc3f4f7f318504a706686281af9
