# [H] CVE-2018-13112

## Summary
Severity: High
Advisory: CVE-2018-13112
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2018-07-03
Source: https://osv.dev/vulnerability/CVE-2018-13112
Type: osv

## Details
get_l2len in common/get.c in Tcpreplay 4.3.0 beta1 allows remote attackers to cause a denial of service (heap-based buffer over-read and application crash) via crafted packets, as demonstrated by tcpprep.

## References
- https://github.com/appneta/tcpreplay/issues/477
