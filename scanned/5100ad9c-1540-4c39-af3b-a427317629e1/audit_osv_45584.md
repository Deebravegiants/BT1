# [H] JLSEC-2026-1330

## Summary
Severity: High
Advisory: JLSEC-2026-1330
Ecosystem: Julia
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2026-08-17
Source: https://osv.dev/vulnerability/JLSEC-2026-1330
Type: osv

## Affected
- Julia: `LibCURL_jll` — affected >=0 <7.71.1+0

## Details
curl 7.62.0 through 7.70.0 is vulnerable to an information disclosure vulnerability that can lead to a partial password being leaked over the network and to the DNS server(s).

## References
- https://cert-portal.siemens.com/productcert/pdf/ssa-200951.pdf
- https://cert-portal.siemens.com/productcert/pdf/ssa-200951.pdf
- https://cert-portal.siemens.com/productcert/pdf/ssa-389290.pdf
- https://cert-portal.siemens.com/productcert/pdf/ssa-389290.pdf
- https://curl.se/docs/CVE-2020-8169.html
- https://curl.se/docs/CVE-2020-8169.html
- https://hackerone.com/reports/874778
- https://hackerone.com/reports/874778
- https://www.debian.org/security/2021/dsa-4881
- https://www.debian.org/security/2021/dsa-4881
