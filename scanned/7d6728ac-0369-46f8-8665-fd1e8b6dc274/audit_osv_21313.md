# [H] CVE-2021-42072

## Summary
Severity: High
Advisory: CVE-2021-42072
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2021-11-08
Source: https://osv.dev/vulnerability/CVE-2021-42072
Type: osv

## Details
An issue was discovered in Barrier before 2.4.0. The barriers component (aka the server-side implementation of Barrier) does not sufficiently verify the identify of connecting clients. Clients can thus exploit weaknesses in the provided protocol to cause denial-of-service or stage further attacks that could lead to information leaks or integrity corruption.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/CIEVNCFEFO7L3NTM4VUZB3WKYYCBTFCI/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/XMU3STOKHPEZSC54MZ42YBFFC2R3BU2Q/
- https://github.com/debauchee/barrier/releases/tag/v2.4.0
- http://www.openwall.com/lists/oss-security/2021/11/02/4
