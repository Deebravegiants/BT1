# [M] CVE-2020-23273

## Summary
Severity: Medium
Advisory: CVE-2020-23273
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2021-09-22
Source: https://osv.dev/vulnerability/CVE-2020-23273
Type: osv

## Details
Heap-buffer overflow in the randomize_iparp function in edit_packet.c. of Tcpreplay v4.3.2 allows attackers to cause a denial of service (DOS) via a crafted pcap.

## References
- https://github.com/appneta/tcpreplay/issues/579
