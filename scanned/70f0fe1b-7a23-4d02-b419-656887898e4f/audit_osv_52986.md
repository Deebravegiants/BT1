# [H] CVE-2022-24122

## Summary
Severity: High
Advisory: CVE-2022-24122
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2022-01-29
Source: https://osv.dev/vulnerability/CVE-2022-24122
Type: osv

## Details
kernel/ucount.c in the Linux kernel 5.14 through 5.16.4, when unprivileged user namespaces are enabled, allows a use-after-free and privilege escalation because a ucounts object can outlive its namespace.

## References
- https://security.netapp.com/advisory/ntap-20220221-0001/
- https://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=f9d87929d451d3e649699d0f1d74f71f77ad38f5
- https://github.com/torvalds/linux/commit/f9d87929d451d3e649699d0f1d74f71f77ad38f5
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/HSR3AI2IQGRKZCHNKF6S25JGDKUEAWWL/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/VVSZKUJAZ2VN6LJ35J2B6YD6BOPQTU3B/
- https://www.openwall.com/lists/oss-security/2022/01/29/1
