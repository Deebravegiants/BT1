# [H] CVE-2019-11490

## Summary
Severity: High
Advisory: CVE-2019-11490
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-04-24
Source: https://osv.dev/vulnerability/CVE-2019-11490
Type: osv

## Details
An issue was discovered in Npcap 0.992. Sending a malformed .pcap file with the loopback adapter using either pcap_sendqueue_queue() or pcap_sendqueue_transmit() results in kernel pool corruption. This could lead to arbitrary code executing inside the Windows kernel and allow escalation of privileges.

## References
- https://github.com/nmap/nmap/issues/1568
