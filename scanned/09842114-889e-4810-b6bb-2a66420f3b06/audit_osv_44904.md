# [M] rclone archive/zip: Zip Slip via unsanitized zip entry names lets a malicious archive escape its own namespace

## Summary
Severity: Medium
Advisory: CVE-2026-88014
Aliases: GHSA-66hp-wgxq-6f5q
CVSS: 6.3 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:C/C:N/I:H/A:N)
Published: 2026-09-10
Source: https://osv.dev/vulnerability/CVE-2026-88014
Type: osv

## Details
rclone is a command-line program to sync files and directories to and from different cloud storage providers. From 1.72.0 until 1.75.1, the archive ZIP backend method (*Fs).readZip in backend/archive/zip/zip.go accepts archive/zip.File.Name values from an untrusted central directory and exposes cleaned entry names without ensuring that they remain inside the archive namespace. Entries such as ../../etc/cron.d/evil can survive path.Clean and become Object.Remote() values that fs/sync and fs/operations use as destination-relative paths, allowing rclone copy or sync to write outside the selected destination on backends that do not independently confine the path. The non-empty root check also used strings.HasPrefix without a path boundary, so root foo could incorrectly include sibling foobar entries. This issue is fixed in version 1.75.1.

## References
- https://github.com/rclone/rclone/releases/tag/v1.75.1
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/88xxx/CVE-2026-88014.json
- https://github.com/rclone/rclone/security/advisories/GHSA-66hp-wgxq-6f5q
- https://nvd.nist.gov/vuln/detail/CVE-2026-88014
- https://github.com/rclone/rclone/commit/5dae3adbf571a6cd9ba501eb47397a7e871e1ae0
- https://github.com/rclone/rclone/commit/6507e13d5a83789f500af96d7188c302c9d74d98
