# [H] RIOT-OS vulnerable to Out of Bounds write in routing with SRH

## Summary
Severity: High
Advisory: CVE-2023-24817
Aliases: GHSA-xjgw-7638-29g5
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2023-05-30
Source: https://osv.dev/vulnerability/CVE-2023-24817
Type: osv

## Details
RIOT-OS, an operating system for Internet of Things (IoT) devices, contains a network stack with the ability to process 6LoWPAN frames. Prior to version 2023.04, an attacker can send a crafted frame to the device resulting in an integer underflow and out of bounds access in the packet buffer. Triggering the access at the right time will corrupt other packets or the allocator metadata. Corrupting a pointer will lead to denial of service. This issue is fixed in version 2023.04. As a workaround, disable SRH in the network stack.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/24xxx/CVE-2023-24817.json
- https://github.com/RIOT-OS/RIOT/security/advisories/GHSA-xjgw-7638-29g5
- https://nvd.nist.gov/vuln/detail/CVE-2023-24817
- https://github.com/RIOT-OS/RIOT/commit/34dc1757f5621be48e226cfebb2f4c63505b5360
