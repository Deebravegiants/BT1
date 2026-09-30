# [H] Apache MINA SSHD: integrity check bypass

## Summary
Severity: High
Advisory: GHSA-2326-hx7g-3m9r
CVE: CVE-2024-41909
CWE: CWE-354
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2024-08-12
Source: https://github.com/advisories/GHSA-2326-hx7g-3m9r
Type: github-advisory

## Affected
- Maven: `org.apache.sshd:sshd-common` — affected >=0 <2.12.0

## Details
Like many other SSH implementations, Apache MINA SSHD suffered from the issue that is more widely known as CVE-2023-48795. An attacker that can intercept traffic between client and server could drop certain packets from the stream, potentially causing client and server to consequently end up with a connection for which 
some security features have been downgraded or disabled, aka a Terrapin 
attack

The mitigations to prevent this type of attack were implemented in Apache MINA SSHD 2.12.0, both client and server side. Users are recommended to upgrade to at least this version. Note that both the client and the server implementation must have mitigations applied against this issue, otherwise the connection may still be affected.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-41909
- https://github.com/apache/mina-sshd/issues/445
- https://github.com/apache/mina-sshd/pull/449
- https://github.com/apache/mina-sshd/commit/315739e4e9d1dc7a4ff32ea64936982ed0b73e76
- https://github.com/apache/mina-sshd/commit/6b0fd46f64bcb75eeeee31d65f10242660aad7c1
- https://github.com/apache/mina-sshd/commit/7b2c781640a7a78a9455b86593a1f63c9e8cab92
- https://github.com/apache/mina-sshd
- https://github.com/apache/mina-sshd/releases/tag/sshd-2.12.0
- https://lists.apache.org/thread/vwf1ot8wx1njyy8n19j5j2tcnjnozt3b
- https://security.netapp.com/advisory/ntap-20241011-0006
