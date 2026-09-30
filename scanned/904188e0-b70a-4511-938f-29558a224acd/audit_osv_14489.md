# [H] CVE-2019-10050

## Summary
Severity: High
Advisory: CVE-2019-10050
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2019-05-13
Source: https://osv.dev/vulnerability/CVE-2019-10050
Type: osv

## Details
A buffer over-read issue was discovered in Suricata 4.1.x before 4.1.4. If the input of the decode-mpls.c function DecodeMPLS is composed only of a packet of source address and destination address plus the correct type field and the right number for shim, an attacker can manipulate the control flow, such that the condition to leave the loop is true. After leaving the loop, the network packet has a length of 2 bytes. There is no validation of this length. Later on, the code tries to read at an empty position, leading to a crash.

## References
- https://lists.openinfosecfoundation.org/pipermail/oisf-announce/
- https://suricata-ids.org/2019/04/30/suricata-4-1-4-released/
