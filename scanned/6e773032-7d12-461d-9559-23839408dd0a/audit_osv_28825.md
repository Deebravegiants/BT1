# [C] Drivers: hv: vmbus: Track decrypted status in vmbus_gpadl

## Summary
Severity: Critical
Advisory: CVE-2024-36912
Ecosystem: Linux
CVSS: 9.6 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:H)
Published: 2024-05-30
Source: https://osv.dev/vulnerability/CVE-2024-36912
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.16.0 <6.1.91, >=6.2.0 <6.6.31, >=6.7.0 <6.8.10

## Details
In the Linux kernel, the following vulnerability has been resolved:

Drivers: hv: vmbus: Track decrypted status in vmbus_gpadl

In CoCo VMs it is possible for the untrusted host to cause
set_memory_encrypted() or set_memory_decrypted() to fail such that an
error is returned and the resulting memory is shared. Callers need to
take care to handle these errors to avoid returning decrypted (shared)
memory to the page allocator, which could lead to functional or security
issues.

In order to make sure callers of vmbus_establish_gpadl() and
vmbus_teardown_gpadl() don't return decrypted/shared pages to
allocators, add a field in struct vmbus_gpadl to keep track of the
decryption status of the buffers. This will allow the callers to
know if they should free or leak the pages.

## References
- https://git.kernel.org/stable/c/1999644d95194d4a58d3e80ad04ce19220a01a81
- https://git.kernel.org/stable/c/211f514ebf1ef5de37b1cf6df9d28a56cfd242ca
- https://git.kernel.org/stable/c/8e62341f5c45b27519b7d193bcc32ada416ad9d8
- https://git.kernel.org/stable/c/bfae56be077ba14311509e70706a13458f87ea99
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/36xxx/CVE-2024-36912.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-36912
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
