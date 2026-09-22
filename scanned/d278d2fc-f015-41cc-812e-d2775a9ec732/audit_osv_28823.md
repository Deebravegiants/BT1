# [H] uio_hv_generic: Don't free decrypted memory

## Summary
Severity: High
Advisory: CVE-2024-36910
Ecosystem: Linux
CVSS: 8.4 (CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-05-30
Source: https://osv.dev/vulnerability/CVE-2024-36910
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.16.0 <6.1.91, >=6.2.0 <6.6.31, >=6.7.0 <6.8.10

## Details
In the Linux kernel, the following vulnerability has been resolved:

uio_hv_generic: Don't free decrypted memory

In CoCo VMs it is possible for the untrusted host to cause
set_memory_encrypted() or set_memory_decrypted() to fail such that an
error is returned and the resulting memory is shared. Callers need to
take care to handle these errors to avoid returning decrypted (shared)
memory to the page allocator, which could lead to functional or security
issues.

The VMBus device UIO driver could free decrypted/shared pages if
set_memory_decrypted() fails. Check the decrypted field in the gpadl
to decide whether to free the memory.

## References
- https://git.kernel.org/stable/c/3d788b2fbe6a1a1a9e3db09742b90809d51638b7
- https://git.kernel.org/stable/c/6466a0f6d235c8a18c602cb587160d7e49876db9
- https://git.kernel.org/stable/c/dabf12bf994318d939f70d47cfda30e47abb2c54
- https://git.kernel.org/stable/c/fe2c58602354fbd60680dc42ac3a0b772cda7d23
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/36xxx/CVE-2024-36910.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-36910
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
