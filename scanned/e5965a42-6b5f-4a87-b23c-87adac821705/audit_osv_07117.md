# [C] BIT-node-2021-22930

## Summary
Severity: Critical
Advisory: BIT-node-2021-22930
Aliases: BIT-node-min-2021-22930, CVE-2021-22930
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-node-2021-22930
Type: osv

## Affected
- Bitnami: `node` — affected >=16.0.0 <16.6.0

## Details
Node.js before 16.6.0, 14.17.4, and 12.22.4 is vulnerable to a use after free attack where an attacker might be able to exploit the memory corruption, to change process behavior.

## References
- https://cert-portal.siemens.com/productcert/pdf/ssa-389290.pdf
- https://hackerone.com/reports/1238162
- https://lists.debian.org/debian-lts-announce/2022/10/msg00006.html
- https://nodejs.org/en/blog/vulnerability/july-2021-security-releases-2/
- https://security.gentoo.org/glsa/202401-02
- https://security.netapp.com/advisory/ntap-20211112-0002/
- https://nvd.nist.gov/vuln/detail/CVE-2021-22930
