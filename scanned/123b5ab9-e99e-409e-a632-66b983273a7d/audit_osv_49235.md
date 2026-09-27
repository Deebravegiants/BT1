# [M] CVE-2018-7273

## Summary
Severity: Medium
Advisory: CVE-2018-7273
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2018-02-21
Source: https://osv.dev/vulnerability/CVE-2018-7273
Type: osv

## Details
In the Linux kernel through 4.15.4, the floppy driver reveals the addresses of kernel functions and global variables using printk calls within the function show_floppy in drivers/block/floppy.c. An attacker can read this information from dmesg and use the addresses to find the locations of kernel code and data and bypass kernel security protections such as KASLR.

## References
- http://www.securityfocus.com/bid/103088
- https://lkml.org/lkml/2018/2/20/669
- https://www.exploit-db.com/exploits/44325/
