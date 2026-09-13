# [H] BIT-node-2021-22940

## Summary
Severity: High
Advisory: BIT-node-2021-22940
Aliases: BIT-node-min-2021-22940, CVE-2021-22940
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-node-2021-22940
Type: osv

## Affected
- Bitnami: `node` — affected >=16.0.0 <16.6.2

## Details
Node.js before 16.6.1, 14.17.5, and 12.22.5 is vulnerable to a use after free attack where an attacker might be able to exploit the memory corruption, to change process behavior.

## References
- https://cert-portal.siemens.com/productcert/pdf/ssa-389290.pdf
- https://hackerone.com/reports/1238162
- https://lists.debian.org/debian-lts-announce/2022/10/msg00006.html
- https://nodejs.org/en/blog/vulnerability/aug-2021-security-releases/
- https://security.gentoo.org/glsa/202401-02
- https://security.netapp.com/advisory/ntap-20210923-0001/
- https://www.oracle.com/security-alerts/cpujan2022.html
- https://www.oracle.com/security-alerts/cpujul2022.html
- https://www.oracle.com/security-alerts/cpuoct2021.html
- https://nvd.nist.gov/vuln/detail/CVE-2021-22940
