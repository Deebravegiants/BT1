# [M] CVE-2020-14416

## Summary
Severity: Medium
Advisory: CVE-2020-14416
CVSS: 4.2 (CVSS:3.1/AV:L/AC:L/PR:H/UI:R/S:U/C:N/I:N/A:H)
Published: 2020-06-18
Source: https://osv.dev/vulnerability/CVE-2020-14416
Type: osv

## Details
In the Linux kernel before 5.4.16, a race condition in tty->disc_data handling in the slip and slcan line discipline could lead to a use-after-free, aka CID-0ace17d56824. This affects drivers/net/slip/slip.c and drivers/net/can/slcan.c.

## References
- http://lists.opensuse.org/opensuse-security-announce/2020-07/msg00008.html
- http://lists.opensuse.org/opensuse-security-announce/2020-08/msg00009.html
- https://cdn.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.4.16
- https://bugzilla.suse.com/show_bug.cgi?id=1162002
- https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/commit/?id=0ace17d56824165c7f4c68785d6b58971db954dd
