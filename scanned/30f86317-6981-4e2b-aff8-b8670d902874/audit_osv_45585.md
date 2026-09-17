# [H] JLSEC-2026-1331

## Summary
Severity: High
Advisory: JLSEC-2026-1331
Ecosystem: Julia
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-17
Source: https://osv.dev/vulnerability/JLSEC-2026-1331
Type: osv

## Affected
- Julia: `LibCURL_jll` — affected >=0 <7.71.1+0

## Details
curl 7.20.0 through 7.70.0 is vulnerable to improper restriction of names for files and other resources that can lead too overwriting a local file when the -J flag is used.

## References
- https://cert-portal.siemens.com/productcert/pdf/ssa-389290.pdf
- https://cert-portal.siemens.com/productcert/pdf/ssa-389290.pdf
- https://curl.se/docs/CVE-2020-8177.html
- https://curl.se/docs/CVE-2020-8177.html
- https://hackerone.com/reports/887462
- https://hackerone.com/reports/887462
- https://www.debian.org/security/2021/dsa-4881
- https://www.debian.org/security/2021/dsa-4881
- https://www.oracle.com/security-alerts/cpujan2022.html
- https://www.oracle.com/security-alerts/cpujan2022.html
