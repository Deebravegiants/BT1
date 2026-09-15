# [M] Race condition exists in the key generation and rotation functionality

## Summary
Severity: Medium
Advisory: CVE-2023-1672
CVSS: 5.3 (CVSS:3.1/AV:A/AC:H/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2023-07-11
Source: https://osv.dev/vulnerability/CVE-2023-1672
Type: osv

## Details
A race condition exists in the Tang server functionality for key generation and key rotation. This flaw results in a small time window where Tang private keys become readable by other processes on the same host.

## References
- https://access.redhat.com/downloads/content/package-browser/
- https://lists.debian.org/debian-lts-announce/2023/11/msg00004.html
- https://packages.fedoraproject.org/
- https://www.openwall.com/lists/oss-security/2023/06/15/1
- https://access.redhat.com/security/cve/CVE-2023-1672
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/1xxx/CVE-2023-1672.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-1672
- https://bugzilla.redhat.com/show_bug.cgi?id=2180999
- https://github.com/latchset/tang/commit/8dbbed10870378f1b2c3cf3df2ea7edca7617096
