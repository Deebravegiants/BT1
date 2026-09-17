# [M] CVE-2020-10737

## Summary
Severity: Medium
Advisory: CVE-2020-10737
CVSS: 6.3 (CVSS:3.1/AV:L/AC:H/PR:H/UI:R/S:U/C:H/I:H/A:H)
Published: 2020-05-27
Source: https://osv.dev/vulnerability/CVE-2020-10737
Type: osv

## Details
A race condition was found in the mkhomedir tool shipped with the oddjob package in versions before 0.34.5 and 0.34.6 wherein, during the home creation, mkhomedir copies the /etc/skel directory into the newly created home and changes its ownership to the home's user without properly checking the homedir path. This flaw allows an attacker to leverage this issue by creating a symlink point to a target folder, which then has its ownership transferred to the new home directory's unprivileged user.

## References
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2020-10737
- https://pagure.io/oddjob/c/10b8aaa1564b723a005b53acc069df71313f4cac?branch
