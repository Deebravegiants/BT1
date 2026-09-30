# [H] RIOT-OS vulnerable to Integer Underflow during defragmentation

## Summary
Severity: High
Advisory: CVE-2023-24821
Aliases: GHSA-2fpr-82xr-p887
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2023-04-24
Source: https://osv.dev/vulnerability/CVE-2023-24821
Type: osv

## Details
RIOT-OS, an operating system that supports Internet of Things devices, contains a network stack with the ability to process 6LoWPAN frames. Prior to version 2022.10, an attacker can send a crafted frame to the device resulting in a large out of bounds write beyond the packet buffer. The write will create a hard fault exception after reaching the last page of RAM. The hard fault is not handled and the system will be stuck until reset, thus the impact is denial of service. Version 2022.10 fixes this issue. As a workaround, disable support for fragmented IP datagrams or apply the patches manually.

## References
- https://github.com/RIOT-OS/RIOT/pull/18817/commits/9728f727e75d7d78dbfb5918e0de1b938b7b6d2c
- https://github.com/RIOT-OS/RIOT/pull/18820/commits/bd31010231f5340e21410595dd95afc86bbfd341
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/24xxx/CVE-2023-24821.json
- https://github.com/RIOT-OS/RIOT/security/advisories/GHSA-2fpr-82xr-p887
- https://nvd.nist.gov/vuln/detail/CVE-2023-24821
