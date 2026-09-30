# [M] CVE-2023-0597

## Summary
Severity: Medium
Advisory: CVE-2023-0597
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2023-02-23
Source: https://osv.dev/vulnerability/CVE-2023-0597
Type: osv

## Details
A flaw possibility of memory leak in the Linux kernel cpu_entry_area mapping of X86 CPU data to memory was found in the way user can guess location of exception stack(s) or other important data. A local user could use this flaw to get access to some important data with expected location in memory.

## References
- http://www.openwall.com/lists/oss-security/2023/07/28/1
- https://www.openwall.com/lists/oss-security/2023/07/28/1
- https://git.kernel.org/linus/97e3d26b5e5f371b3ee223d94dd123e6c442ba80
