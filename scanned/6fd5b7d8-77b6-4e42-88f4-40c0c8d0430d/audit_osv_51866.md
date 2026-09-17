# [M] CVE-2021-43389

## Summary
Severity: Medium
Advisory: CVE-2021-43389
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2021-11-04
Source: https://osv.dev/vulnerability/CVE-2021-43389
Type: osv

## Details
An issue was discovered in the Linux kernel before 5.14.15. There is an array-index-out-of-bounds flaw in the detach_capi_ctr function in drivers/isdn/capi/kcapi.c.

## References
- https://lore.kernel.org/netdev/CAFcO6XOvGQrRTaTkaJ0p3zR7y7nrAWD79r48=L_BbOyrK9X-vA%40mail.gmail.com/
- https://cdn.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.14.15
- http://www.openwall.com/lists/oss-security/2021/11/05/1
- https://lists.debian.org/debian-lts-announce/2021/12/msg00012.html
- https://lists.debian.org/debian-lts-announce/2022/03/msg00012.html
- https://www.debian.org/security/2022/dsa-5096
- https://www.oracle.com/security-alerts/cpujul2022.html
- https://bugzilla.redhat.com/show_bug.cgi?id=2013180
- https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/commit/?id=1f3e2e97c003f80c4b087092b225c8787ff91e4d
- https://seclists.org/oss-sec/2021/q4/39
