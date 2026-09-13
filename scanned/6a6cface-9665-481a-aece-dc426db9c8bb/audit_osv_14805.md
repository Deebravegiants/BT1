# [H] CVE-2019-11503

## Summary
Severity: High
Advisory: CVE-2019-11503
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N)
Published: 2019-04-24
Source: https://osv.dev/vulnerability/CVE-2019-11503
Type: osv

## Details
snap-confine as included in snapd before 2.39 did not guard against symlink races when performing the chdir() to the current working directory of the calling user, aka a "cwd restore permission bypass."

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/6VACEKVQ7UAZ32WO4ZKCFW6YOBSYJ76L/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/VPU6APEZHAA7N2AI57OT4J2P7NKHFOLM/
- http://www.openwall.com/lists/oss-security/2019/04/25/7
- https://github.com/snapcore/snapd/pull/6642
- https://www.openwall.com/lists/oss-security/2019/04/18/4
