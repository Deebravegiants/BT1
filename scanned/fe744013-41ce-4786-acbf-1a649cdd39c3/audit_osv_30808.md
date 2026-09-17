# [H] efi/libstub: Free correct pointer on failure

## Summary
Severity: High
Advisory: CVE-2024-56573
Ecosystem: Linux
CVSS: 7.0 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-12-27
Source: https://osv.dev/vulnerability/CVE-2024-56573
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.2.0 <6.6.64, >=6.7.0 <6.12.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

efi/libstub: Free correct pointer on failure

cmdline_ptr is an out parameter, which is not allocated by the function
itself, and likely points into the caller's stack.

cmdline refers to the pool allocation that should be freed when cleaning
up after a failure, so pass this instead to free_pool().

## References
- https://git.kernel.org/stable/c/06d39d79cbd5a91a33707951ebf2512d0e759847
- https://git.kernel.org/stable/c/d173aee5709bd0994d216d60589ec67f8b11376a
- https://git.kernel.org/stable/c/eaafbcf0a5782ae412ca7de12ef83fc48ccea4cf
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/56xxx/CVE-2024-56573.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-56573
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
