# [C] rclone: RC per-server auth-proxy bypass

## Summary
Severity: Critical
Advisory: CVE-2026-88044
Aliases: GHSA-p569-5gjg-9cmj
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N)
Published: 2026-09-10
Source: https://osv.dev/vulnerability/CVE-2026-88044
Type: osv

## Details
rclone is a command-line program to sync files and directories to and from different cloud storage providers. From 1.70.0 until 1.75.1, the serve/start RC interface accepts per-server proxyOpt.AuthProxy settings, and the FTP and S3 constructors in cmd/serve/ftp/ftp.go and cmd/serve/s3/server.go incorrectly check the process-global proxy.Opt.AuthProxy value instead. When the global value is empty, the request-local authentication proxy is ignored: FTP falls back to the fixed filesystem with username anonymous and any password, while S3 with AuthKey serves the fixed RC fs rather than the backend selected by the proxy. The dedicated command-line servers that configure the global option are not affected. This issue is fixed in version 1.75.1.

## References
- https://github.com/rclone/rclone/releases/tag/v1.75.1
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/88xxx/CVE-2026-88044.json
- https://github.com/rclone/rclone/security/advisories/GHSA-p569-5gjg-9cmj
- https://nvd.nist.gov/vuln/detail/CVE-2026-88044
- https://github.com/rclone/rclone/commit/739403963abf6f58003c2becd5f7c4ad0d644153
