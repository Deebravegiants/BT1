# [H] CVE-2023-3640

## Summary
Severity: High
Advisory: CVE-2023-3640
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2023-07-24
Source: https://osv.dev/vulnerability/CVE-2023-3640
Type: osv

## Details
A possible unauthorized memory access flaw was found in the Linux kernel's cpu_entry_area mapping of X86 CPU data to memory, where a user may guess the location of exception stacks or other important data. Based on the previous CVE-2023-0597, the 'Randomize per-cpu entry area' feature was implemented in /arch/x86/mm/cpu_entry_area.c, which works through the init_cea_offsets() function when KASLR is enabled. However, despite this feature, there is still a risk of per-cpu entry area leaks. This issue could allow a local user to gain access to some important data with memory in an expected location and potentially escalate their privileges on the system.

## References
- https://access.redhat.com/errata/RHSA-2023:6583
- https://access.redhat.com/security/cve/CVE-2023-3640
- https://bugzilla.redhat.com/show_bug.cgi?id=2217523
