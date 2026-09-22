# [C] RIOT-OS vulnerable to Packet Type Confusion during IPHC send

## Summary
Severity: Critical
Advisory: CVE-2023-24823
Aliases: GHSA-jwmv-47p2-hgq2
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2023-04-24
Source: https://osv.dev/vulnerability/CVE-2023-24823
Type: osv

## Details
RIOT-OS, an operating system that supports Internet of Things devices, contains a network stack with the ability to process 6LoWPAN frames. Prior to version 2022.10, an attacker can send a crafted frame to the device resulting in a type confusion between IPv6 extension headers and a UDP header. This occurs while encoding a 6LoWPAN IPHC header. The type confusion manifests in an out of bounds write in the packet buffer. The overflow can be used to corrupt other packets and the allocator metadata. Corrupting a pointer will easily lead to denial of service. While carefully manipulating the allocator metadata gives an attacker the possibility to write data to arbitrary locations and thus execute arbitrary code. Version 2022.10 fixes this issue. As a workaround, apply the patches manually.

## References
- https://github.com/RIOT-OS/RIOT/pull/18817/commits/4a081f86616cb5c9dd0b5d7b286da03285d1652a
- https://github.com/RIOT-OS/RIOT/pull/18820/commits/dafc397fdc3655aeb5c7b9963a43f1604c6a2062
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/24xxx/CVE-2023-24823.json
- https://github.com/RIOT-OS/RIOT/security/advisories/GHSA-jwmv-47p2-hgq2
- https://nvd.nist.gov/vuln/detail/CVE-2023-24823
