# [C] Command injection vulnerability in programing languages on Microsoft Windows operating system.

## Summary
Severity: Critical
Advisory: BIT-node-2024-3566
Aliases: BIT-node-min-2024-3566, CVE-2024-3566, HSEC-2024-0003
Ecosystem: Bitnami
Published: 2025-06-18
Source: https://osv.dev/vulnerability/BIT-node-2024-3566
Type: osv

## Affected
- Bitnami: `node` — affected >=1.77.2 <18.19.0

## Details
A command inject vulnerability allows an attacker to perform command injection on Windows applications that indirectly depend on the CreateProcess function when the specific conditions are satisfied.

## References
- https://flatt.tech/research/posts/batbadbut-you-cant-securely-execute-commands-on-windows/
- https://kb.cert.org/vuls/id/123335
- https://learn.microsoft.com/en-us/archive/blogs/twistylittlepassagesallalike/everyone-quotes-command-line-arguments-the-wrong-way
- https://nvd.nist.gov/vuln/detail/CVE-2024-3566
- https://www.cve.org/CVERecord?id=CVE-2024-1874
- https://www.cve.org/CVERecord?id=CVE-2024-22423
- https://www.cve.org/CVERecord?id=CVE-2024-24576
- https://www.kb.cert.org/vuls/id/123335
