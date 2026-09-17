# [H] RIOT-OS vulnerable to Null Pointer dereference during IPHC encoding

## Summary
Severity: High
Advisory: CVE-2023-24822
Aliases: GHSA-8x69-5fhj-72wh
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2023-04-24
Source: https://osv.dev/vulnerability/CVE-2023-24822
Type: osv

## Details
RIOT-OS, an operating system that supports Internet of Things devices, contains a network stack with the ability to process 6LoWPAN frames. Prior to version 2022.10, an attacker can send a crafted frame to the device resulting in a NULL pointer dereference while encoding a 6LoWPAN IPHC header. The NULL pointer dereference causes a hard fault exception, leading to denial of service. Version 2022.10 fixes this issue. As a workaround, apply the patches manually.

## References
- https://github.com/RIOT-OS/RIOT/pull/18817/commits/639c04325de4ceb9d444955f4927bfae95843a39
- https://github.com/RIOT-OS/RIOT/pull/18820/commits/7253e261556f252816f4a3b7c4f96fc10d642485
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/24xxx/CVE-2023-24822.json
- https://github.com/RIOT-OS/RIOT/security/advisories/GHSA-8x69-5fhj-72wh
- https://nvd.nist.gov/vuln/detail/CVE-2023-24822
