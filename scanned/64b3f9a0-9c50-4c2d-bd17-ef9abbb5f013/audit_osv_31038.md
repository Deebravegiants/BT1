# [C] virt: tdx-guest: Just leak decrypted memory on unrecoverable errors

## Summary
Severity: Critical
Advisory: CVE-2024-57793
Ecosystem: Linux
CVSS: 9.3 (CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:H)
Published: 2025-01-11
Source: https://osv.dev/vulnerability/CVE-2024-57793
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.7.0 <6.12.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

virt: tdx-guest: Just leak decrypted memory on unrecoverable errors

In CoCo VMs it is possible for the untrusted host to cause
set_memory_decrypted() to fail such that an error is returned
and the resulting memory is shared. Callers need to take care
to handle these errors to avoid returning decrypted (shared)
memory to the page allocator, which could lead to functional
or security issues.

Leak the decrypted memory when set_memory_decrypted() fails,
and don't need to print an error since set_memory_decrypted()
will call WARN_ONCE().

## References
- https://git.kernel.org/stable/c/1429ae7b7d4759a1e362456b8911c701bae655b4
- https://git.kernel.org/stable/c/27834971f616c5e154423c578fa95e0444444ce1
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/57xxx/CVE-2024-57793.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-57793
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
