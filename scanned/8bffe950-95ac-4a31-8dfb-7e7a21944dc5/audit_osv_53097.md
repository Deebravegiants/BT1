# [H] CVE-2022-28733

## Summary
Severity: High
Advisory: CVE-2022-28733
CVSS: 8.1 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2023-07-20
Source: https://osv.dev/vulnerability/CVE-2022-28733
Type: osv

## Details
Integer underflow in grub_net_recv_ip4_packets; A malicious crafted IP packet can lead to an integer underflow in grub_net_recv_ip4_packets() function on rsm->total_len value. Under certain circumstances the total_len value may end up wrapping around to a small integer number which will be used in memory allocation. If the attack succeeds in such way, subsequent operations can write past the end of the buffer.

## References
- https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2022-28733
- https://security.netapp.com/advisory/ntap-20230825-0002/
- https://www.openwall.com/lists/oss-security/2022/06/07/5
