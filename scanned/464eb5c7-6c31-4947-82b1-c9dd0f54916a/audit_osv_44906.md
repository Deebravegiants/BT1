# [H] rclone: Directory metadata (chmod/chown/chtimes) applied through a planted symlink in rclone local --links escapes the destination

## Summary
Severity: High
Advisory: CVE-2026-88016
Aliases: GHSA-f8g7-2xjc-7mfh
CVSS: 7.1 (CVSS:3.1/AV:N/AC:H/PR:L/UI:R/S:C/C:L/I:H/A:L)
Published: 2026-09-10
Source: https://osv.dev/vulnerability/CVE-2026-88016
Type: osv

## Details
rclone is a command-line program to sync files and directories to and from different cloud storage providers. Prior to 1.75.1, when backend/local runs with --links, a source .rclonelink object can plant a symlink in the destination and later directory metadata is applied through that path. MkdirMetadata, writeMetadataToFile, and setTimes operate when Directory.translatedLink=false, so os.Chown, os.Chmod, os.Chtimes, and birth-time handling can bypass os.Root confinement and follow the symlink. An attacker controlling source contents can therefore apply selected ownership, permissions, modification times, or birth times to a file or directory outside the destination, with --metadata required for chmod and chown while modification time is applied by the normal directory workflow. This issue is fixed in version 1.75.1.

## References
- https://github.com/rclone/rclone/releases/tag/v1.75.1
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/88xxx/CVE-2026-88016.json
- https://github.com/rclone/rclone/security/advisories/GHSA-f8g7-2xjc-7mfh
- https://nvd.nist.gov/vuln/detail/CVE-2026-88016
- https://github.com/rclone/rclone/commit/17b0c03338a857bcb0a68d2d4c82ddbdec3f7893
- https://github.com/rclone/rclone/commit/a7ab39d3d1958afa1446982c1dc4e4a73a887e3e
