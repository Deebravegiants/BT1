# [H] CVE-2020-14004

## Summary
Severity: High
Advisory: CVE-2020-14004
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2020-06-12
Source: https://osv.dev/vulnerability/CVE-2020-14004
Type: osv

## Details
An issue was discovered in Icinga2 before v2.12.0-rc1. The prepare-dirs script (run as part of the icinga2 systemd service) executes chmod 2750 /run/icinga2/cmd. /run/icinga2 is under control of an unprivileged user by default. If /run/icinga2/cmd is a symlink, then it will by followed and arbitrary files can be changed to mode 2750 by the unprivileged icinga2 user.

## References
- http://lists.opensuse.org/opensuse-security-announce/2020-11/msg00014.html
- https://github.com/Icinga/icinga2/compare/v2.12.0-rc1...master
- https://github.com/Icinga/icinga2/releases
- https://bugzilla.suse.com/show_bug.cgi?id=CVE-2020-14004
- https://github.com/Icinga/icinga2/pull/8045/commits/2f0f2e8c355b75fa4407d23f85feea037d2bc4b6
- http://www.openwall.com/lists/oss-security/2020/06/12/1
