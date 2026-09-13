# [M] Insecure Temporary File usage in github.com/golang/glog

## Summary
Severity: Medium
Advisory: GHSA-6wxm-mpqj-6jpf
CVE: CVE-2024-45339
CWE: CWE-377, CWE-61
Ecosystem: Go
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2025-01-28
Source: https://github.com/advisories/GHSA-6wxm-mpqj-6jpf
Type: github-advisory

## Affected
- Go: `github.com/golang/glog` — affected >=0 <1.2.4

## Details
When logs are written to a widely-writable directory (the default), an unprivileged attacker may predict a privileged process's log file path and pre-create a symbolic link to a sensitive file in its place. When that privileged process runs, it will follow the planted symlink and overwrite that sensitive file. To fix that, glog now causes the program to exit (with status code 2) when it finds that the configured log file already exists.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-45339
- https://github.com/golang/glog/pull/74
- https://github.com/golang/glog/pull/74/commits/b8741656e406e66d6992bc2c9575e460ecaa0ec2
- https://github.com/golang/glog
- https://groups.google.com/g/golang-announce/c/H-Q4ouHWyKs
- https://lists.debian.org/debian-lts-announce/2025/02/msg00019.html
- https://owasp.org/www-community/vulnerabilities/Insecure_Temporary_File
- https://pkg.go.dev/vuln/GO-2025-3372
