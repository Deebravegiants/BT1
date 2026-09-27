# [M] When saving HSTS data to an excessively long file name, curl could end up removing all contents,...

## Summary
Severity: Medium
Advisory: JLSEC-2026-1343
Ecosystem: Julia
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N)
Published: 2026-08-17
Source: https://osv.dev/vulnerability/JLSEC-2026-1343
Type: osv

## Affected
- Julia: `LibCURL_jll` — affected >=7.84.0+0 <8.5.0+0

## Details
When saving HSTS data to an excessively long file name, curl could end up
removing all contents, making subsequent requests using that file unaware of
the HSTS status they should otherwise use.

## References
- https://cert-portal.siemens.com/productcert/html/ssa-082556.html
- https://cert-portal.siemens.com/productcert/html/ssa-093430.html
- https://cert-portal.siemens.com/productcert/html/ssa-331112.html
- https://curl.se/docs/CVE-2023-46219.html
- https://github.com/advisories/GHSA-fj44-3xpp-9cx2
- https://hackerone.com/reports/2236133
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/3ZX3VW67N4ACRAPMV2QS2LVYGD7H2MVE
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/3ZX3VW67N4ACRAPMV2QS2LVYGD7H2MVE/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/UOGXU25FMMT2X6UUITQ7EZZYMJ42YWWD
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/UOGXU25FMMT2X6UUITQ7EZZYMJ42YWWD/
- https://nvd.nist.gov/vuln/detail/CVE-2023-46219
- https://security.netapp.com/advisory/ntap-20240119-0007
- https://security.netapp.com/advisory/ntap-20240119-0007/
- https://www.debian.org/security/2023/dsa-5587
