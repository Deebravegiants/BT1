# [C] RIOT-OS vulnerable to Buffer Overflow during IPHC receive

## Summary
Severity: Critical
Advisory: CVE-2023-24819
Aliases: GHSA-fv97-2448-gcf6
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2023-04-24
Source: https://osv.dev/vulnerability/CVE-2023-24819
Type: osv

## Details
RIOT-OS, an operating system that supports Internet of Things devices, contains a network stack with the ability to process 6LoWPAN frames. Prior to version 2022.10, an attacker can send a crafted frame to the device resulting in an out of bounds write in the packet buffer. The overflow can be used to corrupt other packets and the allocator metadata. Corrupting a pointer will easily lead to denial of service. While carefully manipulating the allocator metadata gives an attacker the possibility to write data to arbitrary locations and thus execute arbitrary code. Version 2022.10 fixes this issue. As a workaround, disable support for fragmented IP datagrams or apply the patches manually.

## References
- https://github.com/RIOT-OS/RIOT/pull/18817/commits/73615161c01fcfbbc7216cf502cabb12c1598ee4
- https://github.com/RIOT-OS/RIOT/pull/18820/commits/da63e45ee94c03a2e08625b04ea618653eab4a9f
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/24xxx/CVE-2023-24819.json
- https://github.com/RIOT-OS/RIOT/security/advisories/GHSA-fv97-2448-gcf6
- https://nvd.nist.gov/vuln/detail/CVE-2023-24819
