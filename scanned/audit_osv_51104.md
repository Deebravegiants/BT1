# [M] CVE-2021-20317

## Summary
Severity: Medium
Advisory: CVE-2021-20317
CVSS: 4.4 (CVSS:3.1/AV:L/AC:L/PR:H/UI:N/S:U/C:N/I:N/A:H)
Published: 2021-09-27
Source: https://osv.dev/vulnerability/CVE-2021-20317
Type: osv

## Details
A flaw was found in the Linux kernel. A corrupted timer tree caused the task wakeup to be missing in the timerqueue_add function in lib/timerqueue.c. This flaw allows a local attacker with special user privileges to cause a denial of service, slowing and eventually stopping the system while running OSP.

## References
- https://cert-portal.siemens.com/productcert/pdf/ssa-222547.pdf
- https://lists.debian.org/debian-lts-announce/2022/03/msg00012.html
- https://www.debian.org/security/2022/dsa-5096
- https://lists.debian.org/debian-lts-announce/2021/12/msg00012.html
- https://bugzilla.redhat.com/show_bug.cgi?id=2005258
- https://git.kernel.org/pub/scm/linux/kernel/git/tip/tip.git/commit/?id=511885d7061eda3eb1faf3f57dcc936ff75863f1
