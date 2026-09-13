# [C] hv_netvsc: Don't free decrypted memory

## Summary
Severity: Critical
Advisory: CVE-2024-36911
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-05-30
Source: https://osv.dev/vulnerability/CVE-2024-36911
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.16.0 <6.6.31, >=6.7.0 <6.8.10

## Details
In the Linux kernel, the following vulnerability has been resolved:

hv_netvsc: Don't free decrypted memory

In CoCo VMs it is possible for the untrusted host to cause
set_memory_encrypted() or set_memory_decrypted() to fail such that an
error is returned and the resulting memory is shared. Callers need to
take care to handle these errors to avoid returning decrypted (shared)
memory to the page allocator, which could lead to functional or security
issues.

The netvsc driver could free decrypted/shared pages if
set_memory_decrypted() fails. Check the decrypted field in the gpadl
to decide whether to free the memory.

## References
- https://git.kernel.org/stable/c/4aaed9dbe8acd2b6114458f0498a617283d6275b
- https://git.kernel.org/stable/c/a56fe611326332bf6b7126e5559590c57dcebad4
- https://git.kernel.org/stable/c/bbf9ac34677b57506a13682b31a2a718934c0e31
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/36xxx/CVE-2024-36911.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-36911
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
