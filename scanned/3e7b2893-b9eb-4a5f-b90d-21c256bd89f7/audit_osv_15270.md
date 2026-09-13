# [H] CVE-2019-14889

## Summary
Severity: High
Advisory: CVE-2019-14889
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2019-12-10
Source: https://osv.dev/vulnerability/CVE-2019-14889
Type: osv

## Details
A flaw was found with the libssh API function ssh_scp_new() in versions before 0.9.3 and before 0.8.8. When the libssh SCP client connects to a server, the scp command, which includes a user-provided path, is executed on the server-side. In case the library is used in a way where users can influence the third parameter of the function, it would become possible for an attacker to inject arbitrary commands, leading to a compromise of the remote target.

## References
- https://lists.debian.org/debian-lts-announce/2023/05/msg00029.html
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/7JJWJTXVWLLJTVHBPGWL7472S5FWXYQR/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/EV2ONSPDJCTDVORCB4UGRQUZQQ46JHRN/
- http://lists.opensuse.org/opensuse-security-announce/2019-12/msg00033.html
- http://lists.opensuse.org/opensuse-security-announce/2020-01/msg00047.html
- https://lists.debian.org/debian-lts-announce/2019/12/msg00020.html
- https://security.gentoo.org/glsa/202003-27
- https://usn.ubuntu.com/4219-1/
- https://www.libssh.org/security/advisories/CVE-2019-14889.txt
- https://www.oracle.com/security-alerts/cpuapr2020.html
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2019-14889
