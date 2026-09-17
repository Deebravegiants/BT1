# [M] CVE-2022-1348

## Summary
Severity: Medium
Advisory: CVE-2022-1348
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2022-05-25
Source: https://osv.dev/vulnerability/CVE-2022-1348
Type: osv

## Details
A vulnerability was found in logrotate in how the state file is created. The state file is used to prevent parallel executions of multiple instances of logrotate by acquiring and releasing a file lock. When the state file does not exist, it is created with world-readable permission, allowing an unprivileged user to lock the state file, stopping any rotation. This flaw affects logrotate versions before 3.20.0.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/1xxx/CVE-2022-1348.json
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/Y7EHGYRE6DSFSBXQIWYDGTSXKO6IFSJQ/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/ZYEB4F37BY6GLEJKP2EPVAVQ6TA3HQKR/
- https://nvd.nist.gov/vuln/detail/CVE-2022-1348
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2022-1348
- http://www.openwall.com/lists/oss-security/2022/05/25/3
- http://www.openwall.com/lists/oss-security/2022/05/25/4
- http://www.openwall.com/lists/oss-security/2022/05/25/5
