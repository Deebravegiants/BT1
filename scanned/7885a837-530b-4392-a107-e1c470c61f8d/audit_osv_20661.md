# [M] CVE-2021-35939

## Summary
Severity: Medium
Advisory: CVE-2021-35939
CVSS: 6.7 (CVSS:3.1/AV:L/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H)
Published: 2022-08-26
Source: https://osv.dev/vulnerability/CVE-2021-35939
Type: osv

## Details
It was found that the fix for CVE-2017-7500 and CVE-2017-7501 was incomplete: the check was only implemented for the parent directory of the file to be created. A local unprivileged user who owns another ancestor directory could potentially use this flaw to gain root privileges. The highest threat from this vulnerability is to data confidentiality and integrity as well as system availability.

## References
- https://access.redhat.com/security/cve/CVE-2021-35939
- https://rpm.org/wiki/Releases/4.18.0
- https://security.gentoo.org/glsa/202210-22
- https://bugzilla.redhat.com/show_bug.cgi?id=1964129
- https://github.com/rpm-software-management/rpm/commit/96ec957e281220f8e137a2d5eb23b83a6377d556
- https://github.com/rpm-software-management/rpm/pull/1919
