# [H] CVE-2020-27187

## Summary
Severity: High
Advisory: CVE-2020-27187
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2020-10-26
Source: https://osv.dev/vulnerability/CVE-2020-27187
Type: osv

## Details
An issue was discovered in KDE Partition Manager 4.1.0 before 4.2.0. The kpmcore_externalcommand helper contains a logic flaw in which the service invoking D-Bus is not properly checked. An attacker on the local machine can replace /etc/fstab, and execute mount and other partitioning related commands, while KDE Partition Manager is running. the mount command can then be used to gain full root privileges.

## References
- https://github.com/KDE/partitionmanager/compare/v4.1.0...v4.2.0
- https://security.gentoo.org/glsa/202011-03
- https://bugzilla.redhat.com/show_bug.cgi?id=1890199
- https://kde.org/info/security/advisory-20201017-1.txt
