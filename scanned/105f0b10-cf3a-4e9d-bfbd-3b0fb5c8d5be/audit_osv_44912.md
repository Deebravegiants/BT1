# [M] rclone: source object names can escape the configured root on upload

## Summary
Severity: Medium
Advisory: CVE-2026-88046
Aliases: GHSA-38xv-hf3p-h7mq
CVSS: 5.3 (CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:U/C:N/I:H/A:N)
Published: 2026-09-10
Source: https://osv.dev/vulnerability/CVE-2026-88046
Type: osv

## Details
rclone is a command-line program to sync files and directories to and from different cloud storage providers. Prior to 1.75.1, rclone core does not reject parent-directory segments in source Object.Remote() values before fs/list, fs/walk, fs/sync, and fs/operations pass those values to destination backends. A flat-keyspace source object store populated with native non-rclone tooling can contain a raw .. key segment, and affected b2, swift, qingstor, oracleobjectstorage, internetarchive, smb, storj, sftp, webdav, ftp, filelu, shade, and sia destinations use path.Join(root, remote) before EncodeDot can neutralize the segment. A copy or upload can therefore escape the configured root into another bucket, share, or path reachable by the victim credential, with sftp and smb potentially reaching other filesystem or share locations under the same login authority. This issue is fixed in version 1.75.1.

## References
- https://github.com/rclone/rclone/releases/tag/v1.75.1
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/88xxx/CVE-2026-88046.json
- https://github.com/rclone/rclone/security/advisories/GHSA-38xv-hf3p-h7mq
- https://nvd.nist.gov/vuln/detail/CVE-2026-88046
- https://github.com/rclone/rclone/commit/57842c5ee4e1407eda06a414a36510cce2db4252
