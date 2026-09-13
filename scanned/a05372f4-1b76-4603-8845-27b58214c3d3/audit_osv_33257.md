# [H] io_uring: fix incorrect io_kiocb reference in io_link_skb

## Summary
Severity: High
Advisory: CVE-2025-39963
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-10-09
Source: https://osv.dev/vulnerability/CVE-2025-39963
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.10.0 <6.12.49, >=6.13.0 <6.16.9

## Details
In the Linux kernel, the following vulnerability has been resolved:

io_uring: fix incorrect io_kiocb reference in io_link_skb

In io_link_skb function, there is a bug where prev_notif is incorrectly
assigned using 'nd' instead of 'prev_nd'. This causes the context
validation check to compare the current notification with itself instead
of comparing it with the previous notification.

Fix by using the correct prev_nd parameter when obtaining prev_notif.

## References
- https://git.kernel.org/stable/c/2c139a47eff8de24e3350dadb4c9d5e3426db826
- https://git.kernel.org/stable/c/50a98ce1ea694f1ff8e87bc2f8f84096d1736f6a
- https://git.kernel.org/stable/c/a89c34babc2e5834aa0905278f26f4dbe4b26b76
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/39xxx/CVE-2025-39963.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-39963
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
