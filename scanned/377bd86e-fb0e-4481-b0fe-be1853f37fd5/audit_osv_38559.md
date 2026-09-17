# [C] NovumOS has Arbitrary Memory Mapping via Syscall 15 (MemoryMapRange)

## Summary
Severity: Critical
Advisory: CVE-2026-40572
Aliases: GHSA-rg7m-6vh7-f4v2
CVSS: 9.0 (CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:N)
Published: 2026-04-18
Source: https://osv.dev/vulnerability/CVE-2026-40572
Type: osv

## Details
NovumOS is a custom 32-bit operating system written in Zig and x86 Assembly. In versions prior to 0.24, Syscall 15 (MemoryMapRange) allows Ring 3 user-mode processes to map arbitrary virtual address ranges into their address space without validating against forbidden regions, including critical kernel structures such as the IDT, GDT, TSS, and page tables. A local attacker can exploit this to modify kernel interrupt handlers, resulting in privilege escalation from user mode to kernel context. This issue has been fixed in version 0.24.

## References
- https://github.com/MinecAnton209/NovumOS/releases/tag/v0.24
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/40xxx/CVE-2026-40572.json
- https://github.com/MinecAnton209/NovumOS/security/advisories/GHSA-rg7m-6vh7-f4v2
- https://nvd.nist.gov/vuln/detail/CVE-2026-40572
