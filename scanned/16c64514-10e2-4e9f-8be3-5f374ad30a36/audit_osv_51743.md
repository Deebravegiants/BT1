# [H] CVE-2021-3864

## Summary
Severity: High
Advisory: CVE-2021-3864
CVSS: 7.0 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2022-08-26
Source: https://osv.dev/vulnerability/CVE-2021-3864
Type: osv

## Details
A flaw was found in the way the dumpable flag setting was handled when certain SUID binaries executed its descendants. The prerequisite is a SUID binary that sets real UID equal to effective UID, and real GID equal to effective GID. The descendant will then have a dumpable value set to 1. As a result, if the descendant process crashes and core_pattern is set to a relative value, its core dump is stored in the current directory with uid:gid permissions. An unprivileged local user with eligible root SUID binary could use this flaw to place core dumps into root-owned directories, potentially resulting in escalation of privileges.

## References
- https://lore.kernel.org/all/20211221021744.864115-1-longman%40redhat.com/
- https://lore.kernel.org/all/20211226150310.GA992%401wt.eu/
- https://lore.kernel.org/lkml/20211228170910.623156-1-wander%40redhat.com/
- https://access.redhat.com/security/cve/CVE-2021-3864
- https://security-tracker.debian.org/tracker/CVE-2021-3864
- https://bugzilla.redhat.com/show_bug.cgi?id=2015046
- https://www.openwall.com/lists/oss-security/2021/10/20/2
