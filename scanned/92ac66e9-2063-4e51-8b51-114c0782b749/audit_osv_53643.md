# [M] CVE-2023-1192

## Summary
Severity: Medium
Advisory: CVE-2023-1192
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2023-11-01
Source: https://osv.dev/vulnerability/CVE-2023-1192
Type: osv

## Details
A use-after-free flaw was found in smb2_is_status_io_timeout() in CIFS in the Linux Kernel. After CIFS transfers response data to a system call, there are still local variable points to the memory region, and if the system call frees it faster than CIFS uses it, CIFS will access a free memory region, leading to a denial of service.

## References
- https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/commit/?id=d527f51331cace562393a8038d870b3e9916686f
- https://access.redhat.com/security/cve/CVE-2023-1192
- https://bugzilla.redhat.com/show_bug.cgi?id=2154178
