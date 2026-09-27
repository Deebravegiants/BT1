# [H] CVE-2015-3146

## Summary
Severity: High
Advisory: CVE-2015-3146
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2016-04-13
Source: https://osv.dev/vulnerability/CVE-2015-3146
Type: osv

## Details
The (1) SSH_MSG_NEWKEYS and (2) SSH_MSG_KEXDH_REPLY packet handlers in package_cb.c in libssh before 0.6.5 do not properly validate state, which allows remote attackers to cause a denial of service (NULL pointer dereference and crash) via a crafted SSH packet.

## References
- http://www.debian.org/security/2016/dsa-3488
- http://www.ubuntu.com/usn/USN-2912-1
- https://www.libssh.org/2015/04/30/libssh-0-6-5-security-and-bugfix-release/
- https://www.libssh.org/security/advisories/CVE-2015-3146.txt
- http://lists.fedoraproject.org/pipermail/package-announce/2015-July/161802.html
- http://lists.fedoraproject.org/pipermail/package-announce/2015-May/158013.html
- https://git.libssh.org/projects/libssh.git/commit/?h=libssh-0.6.5&id=94f6955fbaee6fda9385a23e505497efe21f5b4f
