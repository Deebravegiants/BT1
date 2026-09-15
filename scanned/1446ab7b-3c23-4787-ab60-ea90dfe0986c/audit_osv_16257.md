# [H] CVE-2019-3836

## Summary
Severity: High
Advisory: CVE-2019-3836
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2019-04-01
Source: https://osv.dev/vulnerability/CVE-2019-3836
Type: osv

## Details
It was discovered in gnutls before version 3.6.7 upstream that there is an uninitialized pointer access in gnutls versions 3.6.3 or later which can be triggered by certain post-handshake messages.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/A3ETBUFBB4G7AITAOUYPGXVMBGVXKUAN/
- https://usn.ubuntu.com/3999-1/
- http://lists.opensuse.org/opensuse-security-announce/2019-05/msg00017.html
- https://access.redhat.com/errata/RHSA-2019:3600
- https://security.gentoo.org/glsa/201904-14
- https://security.netapp.com/advisory/ntap-20190502-0005/
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2019-3836
- https://gitlab.com/gnutls/gnutls/issues/704
