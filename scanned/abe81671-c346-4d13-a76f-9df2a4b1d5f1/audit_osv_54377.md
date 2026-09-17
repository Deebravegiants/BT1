# [M] CVE-2023-5366

## Summary
Severity: Medium
Advisory: CVE-2023-5366
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:N)
Published: 2023-10-06
Source: https://osv.dev/vulnerability/CVE-2023-5366
Type: osv

## Details
A flaw was found in Open vSwitch that allows ICMPv6 Neighbor Advertisement packets between virtual machines to bypass OpenFlow rules. This issue may allow a local attacker to create specially crafted packets with a modified or spoofed target IP address field that can redirect ICMPv6 traffic to arbitrary IP addresses.

## References
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/VYYUBF6OW2JG7VOFEOROHXGSJCTES3QO/
- http://www.openwall.com/lists/oss-security/2024/02/08/4
- https://lists.debian.org/debian-lts-announce/2024/02/msg00004.html
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/LFZADABUDOFI2KZIRQBYFZCIKH55RGY3/
- https://access.redhat.com/security/cve/CVE-2023-5366
- https://bugzilla.redhat.com/show_bug.cgi?id=2006347
