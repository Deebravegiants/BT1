# [M] CVE-2022-41861

## Summary
Severity: Medium
Advisory: CVE-2022-41861
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2023-01-17
Source: https://osv.dev/vulnerability/CVE-2022-41861
Type: osv

## Details
A flaw was found in freeradius. A malicious RADIUS client or home server can send a malformed abinary attribute which can cause the server to crash.

## References
- https://freeradius.org/security/
- https://lists.debian.org/debian-lts-announce/2025/06/msg00030.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/41xxx/CVE-2022-41861.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-41861
- https://github.com/FreeRADIUS/freeradius-server/commit/0ec2b39d260e
