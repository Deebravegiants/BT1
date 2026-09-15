# [M] libssh global known_hosts override

## Summary
Severity: Medium
Advisory: CVE-2025-15079
Aliases: CURL-CVE-2025-15079
CVSS: 5.3 (CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:U/C:H/I:N/A:N)
Published: 2026-01-08
Source: https://osv.dev/vulnerability/CVE-2025-15079
Type: osv

## Details
When doing SSH-based transfers using either SCP or SFTP, and setting the
known_hosts file, libcurl could still mistakenly accept connecting to hosts
*not present* in the specified file if they were added as recognized in the
libssh *global* known_hosts file.

## References
- http://www.openwall.com/lists/oss-security/2026/01/07/6
- https://curl.se/docs/CVE-2025-15079.html
- https://curl.se/docs/CVE-2025-15079.json
- https://hackerone.com/reports/3477116
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/15xxx/CVE-2025-15079.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-15079
