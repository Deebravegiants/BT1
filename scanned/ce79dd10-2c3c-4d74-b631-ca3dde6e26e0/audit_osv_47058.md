# [C] CVE-2015-8833

## Summary
Severity: Critical
Advisory: CVE-2015-8833
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2016-04-12
Source: https://osv.dev/vulnerability/CVE-2015-8833
Type: osv

## Details
Use-after-free vulnerability in the create_smp_dialog function in gtk-dialog.c in the Off-the-Record Messaging (OTR) pidgin-otr plugin before 4.0.2 for Pidgin allows remote attackers to execute arbitrary code via vectors related to the "Authenticate buddy" menu item.

## References
- http://www.debian.org/security/2016/dsa-3528
- https://security.gentoo.org/glsa/201701-10
- https://blog.fuzzing-project.org/39-Heap-use-after-free-in-Pidgin-OTR-plugin-CVE-2015-8833.html
- http://lists.opensuse.org/opensuse-security-announce/2016-03/msg00095.html
- http://lists.opensuse.org/opensuse-updates/2016-03/msg00109.html
- http://www.openwall.com/lists/oss-security/2016/03/09/13
- http://www.openwall.com/lists/oss-security/2016/03/09/8
- http://www.securityfocus.com/bid/84295
- https://bugs.otr.im/issues/128
- https://bugs.otr.im/issues/88
- https://bugs.otr.im/projects/pidgin-otr/repository/revisions/aaf551b9dd5cbba8c4abaa3d4dc7ead860efef94
- https://lists.cypherpunks.ca/pipermail/otr-users/2016-March/002582.html
