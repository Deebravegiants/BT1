# [M] CVE-2016-8569

## Summary
Severity: Medium
Advisory: CVE-2016-8569
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-02-03
Source: https://osv.dev/vulnerability/CVE-2016-8569
Type: osv

## Details
The git_oid_nfmt function in commit.c in libgit2 before 0.24.3 allows remote attackers to cause a denial of service (NULL pointer dereference) via a cat-file command with a crafted object file.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/4E77DG5KGQ7L34U75QY7O6NIPKZNQHQJ/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/X3JBSNJAXP7JA3TGE2NPNRTD77JXFG4E/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/XVUEIG6EESZB6BRU2IE3F5NRUEHMAEKC/
- http://lists.opensuse.org/opensuse-updates/2016-12/msg00075.html
- http://lists.opensuse.org/opensuse-updates/2017-01/msg00103.html
- http://lists.opensuse.org/opensuse-updates/2017-01/msg00110.html
- http://lists.opensuse.org/opensuse-updates/2017-01/msg00114.html
- http://www.securityfocus.com/bid/93465
- https://bugzilla.redhat.com/show_bug.cgi?id=1383211
- http://www.openwall.com/lists/oss-security/2016/10/08/7
- https://github.com/libgit2/libgit2/issues/3937
- https://github.com/libgit2/libgit2/releases/tag/v0.24.3
