# [M] CVE-2017-18360

## Summary
Severity: Medium
Advisory: CVE-2017-18360
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2019-01-31
Source: https://osv.dev/vulnerability/CVE-2017-18360
Type: osv

## Details
In change_port_settings in drivers/usb/serial/io_ti.c in the Linux kernel before 4.11.3, local users could cause a denial of service by division-by-zero in the serial device layer by trying to set very high baud rates.

## References
- https://cdn.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.11.3
- https://usn.ubuntu.com/3933-1/
- https://usn.ubuntu.com/3933-2/
- http://www.securityfocus.com/bid/106802
- https://bugzilla.suse.com/show_bug.cgi?id=1123706
- https://github.com/torvalds/linux/commit/6aeb75e6adfaed16e58780309613a578fe1ee90b
- http://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=6aeb75e6adfaed16e58780309613a578fe1ee90b
