# [M] CVE-2018-7191

## Summary
Severity: Medium
Advisory: CVE-2018-7191
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2019-05-17
Source: https://osv.dev/vulnerability/CVE-2018-7191
Type: osv

## Details
In the tun subsystem in the Linux kernel before 4.13.14, dev_get_valid_name is not called before register_netdevice. This allows local users to cause a denial of service (NULL pointer dereference and panic) via an ioctl(TUNSETIFF) call with a dev name containing a / character. This is similar to CVE-2013-4343.

## References
- http://lists.opensuse.org/opensuse-security-announce/2019-05/msg00071.html
- http://lists.opensuse.org/opensuse-security-announce/2019-06/msg00039.html
- http://www.securityfocus.com/bid/108380
- http://lists.opensuse.org/opensuse-security-announce/2019-06/msg00048.html
- https://cdn.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.13.14
- https://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=0ad646c81b2182f7fa67ec0c8c825e0ee165696d
- https://github.com/torvalds/linux/commit/0ad646c81b2182f7fa67ec0c8c825e0ee165696d
- https://github.com/torvalds/linux/commit/5c25f65fd1e42685f7ccd80e0621829c105785d9
- https://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=5c25f65fd1e42685f7ccd80e0621829c105785d9
- https://bugs.launchpad.net/ubuntu/+source/linux/+bug/1748846
- https://bugs.launchpad.net/ubuntu/+source/linux/+bug/1743792
