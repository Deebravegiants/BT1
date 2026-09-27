# [M] CVE-2018-1116

## Summary
Severity: Medium
Advisory: CVE-2018-1116
CVSS: 4.4 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:L)
Published: 2018-07-10
Source: https://osv.dev/vulnerability/CVE-2018-1116
Type: osv

## Details
A flaw was found in polkit before version 0.116. The implementation of the polkit_backend_interactive_authority_check_authorization function in polkitd allows to test for authentication and trigger authentication of unrelated processes owned by other users. This may result in a local DoS and information disclosure.

## References
- https://lists.debian.org/debian-lts-announce/2018/07/msg00042.html
- https://security.gentoo.org/glsa/201908-14
- https://usn.ubuntu.com/3717-2/
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2018-1116
- https://cgit.freedesktop.org/polkit/commit/?id=bc7ffad5364
