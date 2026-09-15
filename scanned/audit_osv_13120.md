# [H] CVE-2018-17580

## Summary
Severity: High
Advisory: CVE-2018-17580
CVSS: 7.1 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:N/A:H)
Published: 2018-09-28
Source: https://osv.dev/vulnerability/CVE-2018-17580
Type: osv

## Details
A heap-based buffer over-read exists in the function fast_edit_packet() in the file send_packets.c of Tcpreplay v4.3.0 beta1. This can lead to Denial of Service (DoS) and potentially Information Exposure when the application attempts to process a crafted pcap file.

## References
- https://github.com/appneta/tcpreplay/issues/485
- https://github.com/SegfaultMasters/covering360/blob/master/tcpreplay
