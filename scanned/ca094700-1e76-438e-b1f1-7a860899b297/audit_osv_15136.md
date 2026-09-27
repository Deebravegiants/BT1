# [H] CVE-2019-1387

## Summary
Severity: High
Advisory: CVE-2019-1387
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2019-12-18
Source: https://osv.dev/vulnerability/CVE-2019-1387
Type: osv

## Details
An issue was found in Git before v2.24.1, v2.23.1, v2.22.2, v2.21.1, v2.20.2, v2.19.3, v2.18.2, v2.17.3, v2.16.6, v2.15.4, and v2.14.6. Recursive clones are currently affected by a vulnerability that is caused by too-lax validation of submodule names, allowing very targeted attacks via remote code execution in recursive clones.

## References
- http://lists.opensuse.org/opensuse-security-announce/2020-01/msg00056.html
- http://lists.opensuse.org/opensuse-security-announce/2020-05/msg00003.html
- https://lists.debian.org/debian-lts-announce/2020/01/msg00019.html
- https://lists.debian.org/debian-lts-announce/2024/06/msg00018.html
- https://lists.debian.org/debian-lts-announce/2024/09/msg00009.html
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/N6UGTEOXWIYSM5KDZL74QD2GK6YQNQCP/
- https://lore.kernel.org/git/xmqqr21cqcn9.fsf%40gitster-ct.c.googlers.com/T/#u
- https://public-inbox.org/git/xmqqr21cqcn9.fsf%40gitster-ct.c.googlers.com/
- https://access.redhat.com/errata/RHSA-2019:4356
- https://access.redhat.com/errata/RHSA-2020:0002
- https://access.redhat.com/errata/RHSA-2020:0124
- https://access.redhat.com/errata/RHSA-2020:0228
- https://security.gentoo.org/glsa/202003-30
- https://security.gentoo.org/glsa/202003-42
