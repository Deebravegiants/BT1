# [H] RIOT-OS vulnerable to null pointer dereference during fragment forwarding

## Summary
Severity: High
Advisory: CVE-2023-24818
Aliases: GHSA-69h9-vj5r-xcg6
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2023-04-24
Source: https://osv.dev/vulnerability/CVE-2023-24818
Type: osv

## Details
RIOT-OS, an operating system that supports Internet of Things devices, contains a network stack with the ability to process 6LoWPAN frames. Prior to version 2022.10, an attacker can send a crafted frame to the device resulting in a NULL pointer dereference. During forwarding of a fragment an uninitialized entry in the reassembly buffer is used. The NULL pointer dereference triggers a hard fault exception resulting in denial of service. Version 2022.10 fixes this issue. As a workaround, disable support for fragmented IP datagrams or apply the patches manually.

## References
- https://github.com/RIOT-OS/RIOT/pull/18817/commits/0bec3e245ed3815ad6c8cae54673f0021777768b
- https://github.com/RIOT-OS/RIOT/pull/18817/commits/17c70f7ee0b1445f2941f516f264ed4a096e82b7
- https://github.com/RIOT-OS/RIOT/pull/18817/commits/aa27ed71fa3e5d48dee1748dcf27b6323ec98a33
- https://github.com/RIOT-OS/RIOT/pull/18820/commits/4b23d93868a28edd8ebf2ff4ebe94540f2475008
- https://github.com/RIOT-OS/RIOT/pull/18820/commits/f4df5b4c4f841ccb460930894cf68ab10b55b971
- https://github.com/RIOT-OS/RIOT/pull/18820/commits/f4fb746d1acaacc962daeed3aa71aadfe307d20e
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/24xxx/CVE-2023-24818.json
- https://github.com/RIOT-OS/RIOT/security/advisories/GHSA-69h9-vj5r-xcg6
- https://nvd.nist.gov/vuln/detail/CVE-2023-24818
