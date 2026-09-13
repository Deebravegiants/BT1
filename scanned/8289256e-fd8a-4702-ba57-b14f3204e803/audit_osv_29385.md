# [H] s390/mm: Add NULL pointer check to crst_table_free() base_crst_free()

## Summary
Severity: High
Advisory: CVE-2024-42235
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-08-07
Source: https://osv.dev/vulnerability/CVE-2024-42235
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.6.0 <6.6.41, >=6.7.0 <6.9.10

## Details
In the Linux kernel, the following vulnerability has been resolved:

s390/mm: Add NULL pointer check to crst_table_free() base_crst_free()

crst_table_free() used to work with NULL pointers before the conversion
to ptdescs.  Since crst_table_free() can be called with a NULL pointer
(error handling in crst_table_upgrade() add an explicit check.

Also add the same check to base_crst_free() for consistency reasons.

In real life this should not happen, since order two GFP_KERNEL
allocations will not fail, unless FAIL_PAGE_ALLOC is enabled and used.

## References
- https://git.kernel.org/stable/c/794fa52b94637d6b2e8c9474fbe3983af5c9f046
- https://git.kernel.org/stable/c/b5efb63acf7bddaf20eacfcac654c25c446eabe8
- https://git.kernel.org/stable/c/f80bd8bb6f380bc265834c46058d38b34174813e
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/42xxx/CVE-2024-42235.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-42235
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
