# [H] rclone: S3 multipart declared-length memory exhaustion

## Summary
Severity: High
Advisory: CVE-2026-88045
Aliases: GHSA-2p48-j3qc-rx9f
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-09-10
Source: https://osv.dev/vulnerability/CVE-2026-88045
Type: osv

## Details
rclone is a command-line program to sync files and directories to and from different cloud storage providers. From 1.75.0 until 1.75.1, the serve S3 streamed multipart path in cmd/serve/s3/multipart.go passes attacker-controlled contentLength to multipart.NewRW().Reserve before reading request-body bytes. waitForTurn admits the current part and one oversized part when the buffer is empty despite --multipart-streaming-buffer-limit, and lib/pool allocates 1 MiB pages according to Content-Length or X-Amz-Decoded-Content-Length. A network client can retain or multiply these reservations without sending the declared body, exhausting process or host memory or permanently blocking request handlers. Anonymous S3 deployments require no credentials, while deployments using auth_key require an accepted S3 key. This issue is fixed in version 1.75.1.

## References
- https://github.com/rclone/rclone/releases/tag/v1.75.1
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/88xxx/CVE-2026-88045.json
- https://github.com/rclone/rclone/security/advisories/GHSA-2p48-j3qc-rx9f
- https://nvd.nist.gov/vuln/detail/CVE-2026-88045
- https://github.com/rclone/rclone/issues/9616
- https://github.com/rclone/rclone/commit/7c1dfd99f3e6a22fcefd8686cc478226a15e63a1
- https://github.com/rclone/rclone/commit/ab1f458013aaf6356e4bdeca61f7cb9139f8eb86
