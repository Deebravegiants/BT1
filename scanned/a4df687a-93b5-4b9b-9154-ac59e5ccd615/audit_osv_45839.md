# [M] JLSEC-2026-393

## Summary
Severity: Medium
Advisory: JLSEC-2026-393
Ecosystem: Julia
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2026-05-04
Source: https://osv.dev/vulnerability/JLSEC-2026-393
Type: osv

## Affected
- Julia: `CURL_jll` — affected >=0 <8.5.0+0
- Julia: `LibCURL_jll` — affected >=0 <7.84.0+0

## Details
curl < 7.84.0 supports "chained" HTTP compression algorithms, meaning that a serverresponse can be compressed multiple times and potentially with different algorithms. The number of acceptable "links" in this "decompression chain" was unbounded, allowing a malicious server to insert a virtually unlimited number of compression steps.The use of such a decompression chain could result in a "malloc bomb", makingcurl end up spending enormous amounts of allocated heap memory, or trying toand returning out of memory errors.

## References
- http://seclists.org/fulldisclosure/2022/Oct/28
- http://seclists.org/fulldisclosure/2022/Oct/41
- http://www.openwall.com/lists/oss-security/2023/02/15/3
- https://cert-portal.siemens.com/productcert/pdf/ssa-333517.pdf
- https://hackerone.com/reports/1570651
- https://lists.debian.org/debian-lts-announce/2022/08/msg00017.html
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/BEV6BR4MTI3CEWK2YU2HQZUW5FAS3FEY/
- https://security.gentoo.org/glsa/202212-01
- https://security.netapp.com/advisory/ntap-20220915-0003/
- https://support.apple.com/kb/HT213488
- https://www.debian.org/security/2022/dsa-5197
