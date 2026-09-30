# [H] CVE-2019-18675

## Summary
Severity: High
Advisory: CVE-2019-18675
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-11-25
Source: https://osv.dev/vulnerability/CVE-2019-18675
Type: osv

## Details
The Linux kernel through 5.3.13 has a start_offset+size Integer Overflow in cpia2_remap_buffer in drivers/media/usb/cpia2/cpia2_core.c because cpia2 has its own mmap implementation. This allows local users (with /dev/video0 access) to obtain read and write permissions on kernel physical pages, which can possibly result in a privilege escalation.

## References
- https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/log/drivers/media/usb/cpia2/cpia2_core.c
- https://security.netapp.com/advisory/ntap-20200103-0001/
- https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/commit/?id=be83bbf806822b1b89e0a0f23cd87cddc409e429
- https://deshal3v.github.io/blog/kernel-research/mmap_exploitation
