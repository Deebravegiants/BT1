# [M] JLSEC-2026-404

## Summary
Severity: Medium
Advisory: JLSEC-2026-404
Ecosystem: Julia
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2026-05-04
Source: https://osv.dev/vulnerability/JLSEC-2026-404
Type: osv

## Affected
- Julia: `CURL_jll` — affected >=0 <8.5.0+0
- Julia: `LibCURL_jll` — affected >=0 <7.88.1+0

## Details
An allocation of resources without limits or throttling vulnerability exists in curl <v7.88.0 based on the "chained" HTTP compression algorithms, meaning that a server response can be compressed multiple times and potentially with differentalgorithms. The number of acceptable "links" in this "decompression chain" wascapped, but the cap was implemented on a per-header basis allowing a maliciousserver to insert a virtually unlimited number of compression steps simply byusing many headers. The use of such a decompression chain could result in a "malloc bomb", making curl end up spending enormous amounts of allocated heap memory, or trying to and returning out of memory errors.

## References
- https://hackerone.com/reports/1826048
- https://lists.debian.org/debian-lts-announce/2023/02/msg00035.html
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/BQKE6TXYDHOTFHLTBZ5X73GTKI7II5KO/
- https://security.gentoo.org/glsa/202310-12
- https://security.netapp.com/advisory/ntap-20230309-0006/
- https://www.debian.org/security/2023/dsa-5365
