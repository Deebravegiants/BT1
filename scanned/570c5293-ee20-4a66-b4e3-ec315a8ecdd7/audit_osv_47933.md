# [H] CVE-2017-15126

## Summary
Severity: High
Advisory: CVE-2017-15126
CVSS: 8.1 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-01-14
Source: https://osv.dev/vulnerability/CVE-2017-15126
Type: osv

## Details
A use-after-free flaw was found in fs/userfaultfd.c in the Linux kernel before 4.13.6. The issue is related to the handling of fork failure when dealing with event messages. Failure to fork correctly can lead to a situation where a fork event will be removed from an already freed list of events with userfaultfd_ctx_put().

## References
- http://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=384632e67e0829deb8015ee6ad916b180049d252
- http://www.securityfocus.com/bid/102516
- https://access.redhat.com/errata/RHSA-2018:0676
- https://access.redhat.com/errata/RHSA-2018:1062
- https://access.redhat.com/security/cve/CVE-2017-15126
- https://github.com/torvalds/linux/commit/384632e67e0829deb8015ee6ad916b180049d252
- https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.13.6
- https://bugzilla.redhat.com/show_bug.cgi?id=1523481
