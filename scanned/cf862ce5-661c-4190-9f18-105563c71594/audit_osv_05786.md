# [H] BIT-guacamole-2023-43826

## Summary
Severity: High
Advisory: BIT-guacamole-2023-43826
Aliases: BIT-guacamole-server-2023-43826, CVE-2023-43826
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-guacamole-2023-43826
Type: osv

## Affected
- Bitnami: `guacamole` — affected >=0 <1.5.3

## Details
Apache Guacamole 1.5.3 and older do not consistently ensure that values received from a VNC server will not result in integer overflow. If a user connects to a malicious or compromised VNC server, specially-crafted data could result in memory corruption, possibly allowing arbitrary code to be executed with the privileges of the running guacd process.Users are recommended to upgrade to version 1.5.4, which fixes this issue.

## References
- http://www.openwall.com/lists/oss-security/2023/12/19/4
- https://lists.apache.org/thread/23gzwftpfgtq97tj6ttmbclry53kmwv6
