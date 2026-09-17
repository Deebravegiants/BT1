# [H] ipmi:msghandler: Fix potential memory corruption in ipmi_create_user()

## Summary
Severity: High
Advisory: CVE-2025-38456
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-07-25
Source: https://osv.dev/vulnerability/CVE-2025-38456
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.19.0 <6.1.146, >=6.2.0 <6.6.99, >=6.7.0 <6.12.39, >=6.13.0 <6.15.7

## Details
In the Linux kernel, the following vulnerability has been resolved:

ipmi:msghandler: Fix potential memory corruption in ipmi_create_user()

The "intf" list iterator is an invalid pointer if the correct
"intf->intf_num" is not found.  Calling atomic_dec(&intf->nr_users) on
and invalid pointer will lead to memory corruption.

We don't really need to call atomic_dec() if we haven't called
atomic_add_return() so update the if (intf->in_shutdown) path as well.

## References
- https://git.kernel.org/stable/c/7c1a6ddb99858e7d68961f74ae27caeeeca67b6a
- https://git.kernel.org/stable/c/9e0d33e75c1604c3fad5586ad4dfa3b2695a3950
- https://git.kernel.org/stable/c/cbc1670297f675854e982d23c8583900ff0cc67a
- https://git.kernel.org/stable/c/e2d5c005dfc96fe857676d1d8ac46b29275cb89b
- https://git.kernel.org/stable/c/fa332f5dc6fc662ad7d3200048772c96b861cf6b
- https://lists.debian.org/debian-lts-announce/2025/10/msg00008.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/38xxx/CVE-2025-38456.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-38456
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
