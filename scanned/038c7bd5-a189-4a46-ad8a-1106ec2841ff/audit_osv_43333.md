# [M] CVE-2026-73282

## Summary
Severity: Medium
Advisory: CVE-2026-73282
CVSS: 4.8 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:L/I:L/A:N)
Published: 2026-08-11
Source: https://osv.dev/vulnerability/CVE-2026-73282
Type: osv

## Details
In ssh in OpenSSH before 10.5, a use-after-free for realloc data can occur if a certain pair of remote-forwarding operations are concurrent.

## References
- https://www.openssh.org/releasenotes.html#10.5
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/73xxx/CVE-2026-73282.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-73282
