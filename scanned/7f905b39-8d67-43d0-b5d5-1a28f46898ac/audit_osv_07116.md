# [M] BIT-node-2021-22918

## Summary
Severity: Medium
Advisory: BIT-node-2021-22918
Aliases: BIT-node-min-2021-22918, CVE-2021-22918
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-node-2021-22918
Type: osv

## Affected
- Bitnami: `node` — affected >=16.0.0 <16.4.1

## Details
Node.js before 16.4.1, 14.17.2, 12.22.2 is vulnerable to an out-of-bounds read when uv__idna_toascii() is used to convert strings to ASCII. The pointer p is read and increased without checking whether it is beyond pe, with the latter holding a pointer to the end of the buffer. This can lead to information disclosures or crashes. This function can be triggered via uv_getaddrinfo().

## References
- https://cert-portal.siemens.com/productcert/pdf/ssa-389290.pdf
- https://hackerone.com/reports/1209681
- https://nodejs.org/en/blog/vulnerability/july-2021-security-releases/
- https://security.gentoo.org/glsa/202401-23
- https://security.netapp.com/advisory/ntap-20210805-0003/
- https://nvd.nist.gov/vuln/detail/CVE-2021-22918
