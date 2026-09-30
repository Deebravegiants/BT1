# [M] Out-of-bounds write when decompressing 6LoWPAN payload in Contiki-NG

## Summary
Severity: Medium
Advisory: CVE-2022-36054
Aliases: GHSA-c36p-vhwg-244c
CVSS: 6.8 (CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:N)
Published: 2022-09-01
Source: https://osv.dev/vulnerability/CVE-2022-36054
Type: osv

## Details
Contiki-NG is an open-source, cross-platform operating system for Next-Generation IoT devices. The 6LoWPAN implementation in the Contiki-NG operating system (file os/net/ipv6/sicslowpan.c) contains an input function that processes incoming packets and copies them into a packet buffer. Because of a missing length check in the input function, it is possible to write outside the packet buffer's boundary. The vulnerability can be exploited by anyone who has the possibility to send 6LoWPAN packets to a Contiki-NG system. In particular, the vulnerability is exposed when sending either of two types of 6LoWPAN packets: an unfragmented packet or the first fragment of a fragmented packet. If the packet is sufficiently large, a subsequent memory copy will cause an out-of-bounds write with data supplied by the attacker.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/36xxx/CVE-2022-36054.json
- https://github.com/contiki-ng/contiki-ng/security/advisories/GHSA-c36p-vhwg-244c
- https://nvd.nist.gov/vuln/detail/CVE-2022-36054
- https://github.com/contiki-ng/contiki-ng/pull/1648
