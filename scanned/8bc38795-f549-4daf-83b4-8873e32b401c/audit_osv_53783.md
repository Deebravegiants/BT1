# [M] CVE-2023-25012

## Summary
Severity: Medium
Advisory: CVE-2023-25012
Aliases: A-268589017, ASB-A-268589017
CVSS: 4.6 (CVSS:3.1/AV:P/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2023-02-02
Source: https://osv.dev/vulnerability/CVE-2023-25012
Type: osv

## Details
The Linux kernel through 6.1.9 has a Use-After-Free in bigben_remove in drivers/hid/hid-bigbenff.c via a crafted USB device because the LED controllers remain registered for too long.

## References
- http://www.openwall.com/lists/oss-security/2023/11/05/1
- https://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=76ca8da989c7d97a7f76c75d475fe95a584439d7
- https://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=27d2a2fd844ec7da70d19fabb482304fd1e0595b
- https://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=9fefb6201c4f8dd9f58c581b2a66e5cde2895ea2
- https://lists.debian.org/debian-lts-announce/2023/05/msg00005.html
- https://lore.kernel.org/all/20230125-hid-unregister-leds-v1-1-9a5192dcef16%40diag.uniroma1.it/
- https://bugzilla.suse.com/show_bug.cgi?id=1207560
- https://seclists.org/oss-sec/2023/q1/53
- http://www.openwall.com/lists/oss-security/2023/02/02/1
