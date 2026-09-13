# [H] fs/proc/task_mmu: prevent integer overflow in pagemap_scan_get_args()

## Summary
Severity: High
Advisory: CVE-2024-53107
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-12-02
Source: https://osv.dev/vulnerability/CVE-2024-53107
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.7.0 <6.11.10

## Details
In the Linux kernel, the following vulnerability has been resolved:

fs/proc/task_mmu: prevent integer overflow in pagemap_scan_get_args()

The "arg->vec_len" variable is a u64 that comes from the user at the start
of the function.  The "arg->vec_len * sizeof(struct page_region))"
multiplication can lead to integer wrapping.  Use size_mul() to avoid
that.

Also the size_add/mul() functions work on unsigned long so for 32bit
systems we need to ensure that "arg->vec_len" fits in an unsigned long.

## References
- https://git.kernel.org/stable/c/669b0cb81e4e4e78cff77a5b367c7f70c0c6c05e
- https://git.kernel.org/stable/c/adee03f8903c58a6a559f21388a430211fac8ce9
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/53xxx/CVE-2024-53107.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-53107
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
