# [H] RIOT-OS vulnerable to Integer Underflow during IPHC receive

## Summary
Severity: High
Advisory: CVE-2023-24820
Aliases: GHSA-vpx8-h94p-9vrj
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2023-04-24
Source: https://osv.dev/vulnerability/CVE-2023-24820
Type: osv

## Details
RIOT-OS, an operating system that supports Internet of Things devices, contains a network stack with the ability to process 6LoWPAN frames. An attacker can send a crafted frame to the device resulting in a large out of bounds write beyond the packet buffer. The write will create a hard fault exception after reaching the last page of RAM. The hard fault is not handled and the system will be stuck until reset. Thus the impact is denial of service. Version 2022.10 fixes this issue. As a workaround, apply the patch manually.

## References
- https://github.com/RIOT-OS/RIOT/pull/18817/commits/2709fbd827b688fe62df2c77c316914f4a3a6d4a
- https://github.com/RIOT-OS/RIOT/pull/18820/commits/d052e2ee166e55bbdfe4c455e65dbd7e3479ebe3
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/24xxx/CVE-2023-24820.json
- https://github.com/RIOT-OS/RIOT/security/advisories/GHSA-vpx8-h94p-9vrj
- https://nvd.nist.gov/vuln/detail/CVE-2023-24820
