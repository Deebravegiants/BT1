# [M] CVE-2022-21499

## Summary
Severity: Medium
Advisory: CVE-2022-21499
CVSS: 6.7 (CVSS:3.1/AV:L/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H)
Published: 2022-06-09
Source: https://osv.dev/vulnerability/CVE-2022-21499
Type: osv

## Details
KGDB and KDB allow read and write access to kernel memory, and thus should be restricted during lockdown. An attacker with access to a serial port could trigger the debugger so it is important that the debugger respect the lockdown mode when/if it is triggered. CVSS 3.1 Base Score 6.7 (Confidentiality, Integrity and Availability impacts). CVSS Vector: (CVSS:3.1/AV:L/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H).

## References
- http://packetstormsecurity.com/files/168191/Kernel-Live-Patch-Security-Notice-LSN-0089-1.html
- https://www.debian.org/security/2022/dsa-5161
- https://git.kernel.org/linus/eadb2f47a3ced5c64b23b90fd2a3463f63726066
