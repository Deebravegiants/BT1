# [C] Drivers: hv: vmbus: Don't free ring buffers that couldn't be re-encrypted

## Summary
Severity: Critical
Advisory: CVE-2024-36909
Ecosystem: Linux
CVSS: 9.3 (CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:H)
Published: 2024-05-30
Source: https://osv.dev/vulnerability/CVE-2024-36909
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.16.0 <6.1.91, >=6.2.0 <6.6.31, >=6.7.0 <6.8.10

## Details
In the Linux kernel, the following vulnerability has been resolved:

Drivers: hv: vmbus: Don't free ring buffers that couldn't be re-encrypted

In CoCo VMs it is possible for the untrusted host to cause
set_memory_encrypted() or set_memory_decrypted() to fail such that an
error is returned and the resulting memory is shared. Callers need to
take care to handle these errors to avoid returning decrypted (shared)
memory to the page allocator, which could lead to functional or security
issues.

The VMBus ring buffer code could free decrypted/shared pages if
set_memory_decrypted() fails. Check the decrypted field in the struct
vmbus_gpadl for the ring buffers to decide whether to free the memory.

## References
- https://git.kernel.org/stable/c/2f622008bf784a9f5dd17baa19223cc2ac30a039
- https://git.kernel.org/stable/c/30d18df6567be09c1433e81993e35e3da573ac48
- https://git.kernel.org/stable/c/82f9e213b124a7d2bb5b16ea35d570260ef467e0
- https://git.kernel.org/stable/c/a9212a4e2963a7fbe3864ba33dc551d4ad8d0abb
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/36xxx/CVE-2024-36909.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-36909
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
