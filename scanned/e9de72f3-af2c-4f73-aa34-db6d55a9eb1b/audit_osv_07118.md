# [M] BIT-node-2021-22939

## Summary
Severity: Medium
Advisory: BIT-node-2021-22939
Aliases: BIT-node-min-2021-22939, CVE-2021-22939
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-node-2021-22939
Type: osv

## Affected
- Bitnami: `node` — affected >=16.0.0 <16.6.2

## Details
If the Node.js https API was used incorrectly and "undefined" was in passed for the "rejectUnauthorized" parameter, no error was returned and connections to servers with an expired certificate would have been accepted.

## References
- https://cert-portal.siemens.com/productcert/pdf/ssa-389290.pdf
- https://hackerone.com/reports/1278254
- https://lists.debian.org/debian-lts-announce/2022/10/msg00006.html
- https://nodejs.org/en/blog/vulnerability/aug-2021-security-releases/
- https://security.gentoo.org/glsa/202401-02
- https://security.netapp.com/advisory/ntap-20210917-0003/
- https://www.oracle.com/security-alerts/cpujan2022.html
- https://www.oracle.com/security-alerts/cpujul2022.html
- https://www.oracle.com/security-alerts/cpuoct2021.html
- https://nvd.nist.gov/vuln/detail/CVE-2021-22939
