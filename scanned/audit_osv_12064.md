# [M] CVE-2018-1000879

## Summary
Severity: Medium
Advisory: CVE-2018-1000879
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2018-12-20
Source: https://osv.dev/vulnerability/CVE-2018-1000879
Type: osv

## Details
libarchive version commit 379867ecb330b3a952fb7bfa7bffb7bbd5547205 onwards (release v3.3.0 onwards) contains a CWE-476: NULL Pointer Dereference vulnerability in ACL parser - libarchive/archive_acl.c, archive_acl_from_text_l() that can result in Crash/DoS. This attack appear to be exploitable via the victim must open a specially crafted archive file.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/CBOCC2M6YGPZA6US43YK4INPSJZZHRTG/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/W645KCLWFDBDGFJHG57WOVXGE62QSIJI/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/ZVXA7PHINVT6DFF6PRLTDTVTXKDLVHNF/
- http://lists.opensuse.org/opensuse-security-announce/2019-04/msg00055.html
- http://www.securityfocus.com/bid/106324
- https://github.com/libarchive/libarchive/pull/1105
- https://bugs.launchpad.net/ubuntu/+source/libarchive/+bug/1794909
- https://github.com/libarchive/libarchive/pull/1105/commits/15bf44fd2c1ad0e3fd87048b3fcc90c4dcff1175
