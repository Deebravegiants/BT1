# [H] CVE-2018-17582

## Summary
Severity: High
Advisory: CVE-2018-17582
CVSS: 7.1 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:N/A:H)
Published: 2018-09-28
Source: https://osv.dev/vulnerability/CVE-2018-17582
Type: osv

## Details
Tcpreplay v4.3.0 beta1 contains a heap-based buffer over-read. The get_next_packet() function in the send_packets.c file uses the memcpy() function unsafely to copy sequences from the source buffer pktdata to the destination (*prev_packet)->pktdata. This will result in a Denial of Service (DoS) and potentially Information Exposure when the application attempts to process a file.

## References
- https://github.com/appneta/tcpreplay/issues/484
- https://github.com/SegfaultMasters/covering360/blob/master/tcpreplay
