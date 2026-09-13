# [M] CVE-2017-6507

## Summary
Severity: Medium
Advisory: CVE-2017-6507
CVSS: 5.9 (CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:H/A:N)
Published: 2017-03-24
Source: https://osv.dev/vulnerability/CVE-2017-6507
Type: osv

## Details
An issue was discovered in AppArmor before 2.12. Incorrect handling of unknown AppArmor profiles in AppArmor init scripts, upstart jobs, and/or systemd unit files allows an attacker to possibly have increased attack surfaces of processes that were intended to be confined by AppArmor. This is due to the common logic to handle 'restart' operations removing AppArmor profiles that aren't found in the typical filesystem locations, such as /etc/apparmor.d/. Userspace projects that manage their own AppArmor profiles in atypical directories, such as what's done by LXD and Docker, are affected by this flaw in the AppArmor init script logic.

## References
- http://www.securityfocus.com/bid/97223
- https://people.canonical.com/~ubuntu-security/cve/2017/CVE-2017-6507.html
- http://bazaar.launchpad.net/~apparmor-dev/apparmor/master/revision/3647
- http://bazaar.launchpad.net/~apparmor-dev/apparmor/master/revision/3648
- https://bugs.launchpad.net/apparmor/+bug/1668892
