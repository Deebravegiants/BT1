# [H] ext4: fix inode use after free in ext4_end_io_rsv_work()

## Summary
Severity: High
Advisory: CVE-2025-38580
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-08-19
Source: https://osv.dev/vulnerability/CVE-2025-38580
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.15.0 <6.15.10, >=6.16.0 <6.16.1

## Details
In the Linux kernel, the following vulnerability has been resolved:

ext4: fix inode use after free in ext4_end_io_rsv_work()

In ext4_io_end_defer_completion(), check if io_end->list_vec is empty to
avoid adding an io_end that requires no conversion to the
i_rsv_conversion_list, which in turn prevents starting an unnecessary
worker. An ext4_emergency_state() check is also added to avoid attempting
to abort the journal in an emergency state.

Additionally, ext4_put_io_end_defer() is refactored to call
ext4_io_end_defer_completion() directly instead of being open-coded.
This also prevents starting an unnecessary worker when EXT4_IO_END_FAILED
is set but data_err=abort is not enabled.

This ensures that the check in ext4_put_io_end_defer() is consistent with
the check in ext4_end_bio(). Otherwise, we might add an io_end to the
i_rsv_conversion_list and then call ext4_finish_bio(), after which the
inode could be freed before ext4_end_io_rsv_work() is called, triggering
a use-after-free issue.

## References
- https://git.kernel.org/stable/c/469c44e66e2110054949609dde095788320139d0
- https://git.kernel.org/stable/c/ac999862b98a0f49e858e509f776be51406f1e77
- https://git.kernel.org/stable/c/c678bdc998754589cea2e6afab9401d7d8312ac4
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/38xxx/CVE-2025-38580.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-38580
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
