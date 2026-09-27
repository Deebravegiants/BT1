# [H] BIT-node-2024-22019

## Summary
Severity: High
Advisory: BIT-node-2024-22019
Aliases: BIT-node-min-2024-22019, CVE-2024-22019
Ecosystem: Bitnami
Published: 2024-05-24
Source: https://osv.dev/vulnerability/BIT-node-2024-22019
Type: osv

## Affected
- Bitnami: `node` — affected >=21.0.0 <21.6.2

## Details
A vulnerability in Node.js HTTP servers allows an attacker to send a specially crafted HTTP request with chunked encoding, leading to resource exhaustion and denial of service (DoS). The server reads an unbounded number of bytes from a single connection, exploiting the lack of limitations on chunk extension bytes. The issue can cause CPU and network bandwidth exhaustion, bypassing standard safeguards like timeouts and body size limits.

## References
- http://www.openwall.com/lists/oss-security/2024/03/11/1
- https://hackerone.com/reports/2233486
- https://security.netapp.com/advisory/ntap-20240315-0004/
- https://nvd.nist.gov/vuln/detail/CVE-2024-22019
- https://lists.debian.org/debian-lts-announce/2024/09/msg00029.html
- https://www.oracle.com/security-alerts/cpuapr2024.html
