# [H] CVE-2021-38604

## Summary
Severity: High
Advisory: CVE-2021-38604
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2021-08-12
Source: https://osv.dev/vulnerability/CVE-2021-38604
Type: osv

## Details
In librt in the GNU C Library (aka glibc) through 2.34, sysdeps/unix/sysv/linux/mq_notify.c mishandles certain NOTIFY_REMOVED data, leading to a NULL pointer dereference. NOTE: this vulnerability was introduced as a side effect of the CVE-2021-33574 fix.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/GYEXYM37RCJWJ6B5KQUYQI4NZBDDYSXP/
- https://sourceware.org/git/?p=glibc.git%3Ba=commit%3Bh=4cc79c217744743077bf7a0ec5e0a4318f1e6641
- https://sourceware.org/git/?p=glibc.git%3Ba=commit%3Bh=b805aebd42364fe696e417808a700fdb9800c9e8
- https://security.gentoo.org/glsa/202208-24
- https://security.netapp.com/advisory/ntap-20210909-0005/
- https://sourceware.org/bugzilla/show_bug.cgi?id=28213
- https://www.oracle.com/security-alerts/cpujul2022.html
- https://blog.tuxcare.com/cve/tuxcare-team-identifies-cve-2021-38604-a-new-vulnerability-in-glibc
