# [M] CVE-2023-1249

## Summary
Severity: Medium
Advisory: CVE-2023-1249
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2023-03-23
Source: https://osv.dev/vulnerability/CVE-2023-1249
Type: osv

## Details
A use-after-free flaw was found in the Linux kernel’s core dump subsystem. This flaw allows a local user to crash the system. Only if patch 390031c94211 ("coredump: Use the vma snapshot in fill_files_note") not applied yet, then kernel could be affected.

## References
- http://packetstormsecurity.com/files/171912/CentOS-Stream-9-Missing-Kernel-Security-Fix.html
- https://patchwork.kernel.org/project/linux-fsdevel/patch/87iltzn3nd.fsf_-_%40email.froward.int.ebiederm.org/
