# [H] CVE-2018-10897

## Summary
Severity: High
Advisory: CVE-2018-10897
CVSS: 8.1 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-08-01
Source: https://osv.dev/vulnerability/CVE-2018-10897
Type: osv

## Details
A directory traversal issue was found in reposync, a part of yum-utils, where reposync fails to sanitize paths in remote repository configuration files. If an attacker controls a repository, they may be able to copy files outside of the destination directory on the targeted system via path traversal. If reposync is running with heightened privileges on a targeted system, this flaw could potentially result in system compromise via the overwriting of critical system files. Version 1.1.31 and older are believed to be affected.

## References
- http://www.securitytracker.com/id/1041594
- https://access.redhat.com/errata/RHSA-2018:2284
- https://access.redhat.com/errata/RHSA-2018:2285
- https://access.redhat.com/errata/RHSA-2018:2626
- https://github.com/rpm-software-management/yum-utils/pull/43
- https://help.ecostruxureit.com/display/public/UADCE725/Security+fixes+in+StruxureWare+Data+Center+Expert+v7.6.0
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2018-10897
- https://github.com/rpm-software-management/yum-utils/commit/6a8de061f8fdc885e74ebe8c94625bf53643b71c
- https://github.com/rpm-software-management/yum-utils/commit/7554c0133eb830a71dc01846037cc047d0acbc2c
