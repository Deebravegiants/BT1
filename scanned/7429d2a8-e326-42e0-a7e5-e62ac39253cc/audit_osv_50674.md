# [M] CVE-2020-27784

## Summary
Severity: Medium
Advisory: CVE-2020-27784
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2022-09-01
Source: https://osv.dev/vulnerability/CVE-2020-27784
Type: osv

## Details
A vulnerability was found in the Linux kernel, where accessing a deallocated instance in printer_ioctl() printer_ioctl() tries to access of a printer_dev instance. However, use-after-free arises because it had been freed by gprinter_free().

## References
- https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/commit/?id=e8d5f92b8d30bb4ade76494490c3c065e12411b1
