# [M] CVE-2018-17974

## Summary
Severity: Medium
Advisory: CVE-2018-17974
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2018-10-03
Source: https://osv.dev/vulnerability/CVE-2018-17974
Type: osv

## Details
An issue was discovered in Tcpreplay 4.3.0 beta1. A heap-based buffer over-read was triggered in the function dlt_en10mb_encode() of the file plugins/dlt_en10mb/en10mb.c, due to inappropriate values in the function memmove(). The length (pktlen + ctx -> l2len) can be larger than source value (packet + ctx->l2len) because the function fails to ensure the length of a packet is valid. This leads to Denial of Service.

## References
- https://github.com/SegfaultMasters/covering360/tree/master/tcpreplay
- https://github.com/appneta/tcpreplay/issues/486
