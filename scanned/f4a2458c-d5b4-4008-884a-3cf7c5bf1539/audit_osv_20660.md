# [M] CVE-2021-35938

## Summary
Severity: Medium
Advisory: CVE-2021-35938
CVSS: 6.7 (CVSS:3.1/AV:L/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H)
Published: 2022-08-25
Source: https://osv.dev/vulnerability/CVE-2021-35938
Type: osv

## Details
A symbolic link issue was found in rpm. It occurs when rpm sets the desired permissions and credentials after installing a file. A local unprivileged user could use this flaw to exchange the original file with a symbolic link to a security-critical file and escalate their privileges on the system. The highest threat from this vulnerability is to data confidentiality and integrity as well as system availability.

## References
- https://access.redhat.com/security/cve/CVE-2021-35938
- https://rpm.org/wiki/Releases/4.18.0
- https://security.gentoo.org/glsa/202210-22
- https://bugzilla.redhat.com/show_bug.cgi?id=1964114
- https://bugzilla.suse.com/show_bug.cgi?id=1157880
- https://github.com/rpm-software-management/rpm/commit/25a435e90844ea98fe5eb7bef22c1aecf3a9c033
- https://github.com/rpm-software-management/rpm/pull/1919
