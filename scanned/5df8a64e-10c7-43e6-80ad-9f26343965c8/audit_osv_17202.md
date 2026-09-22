# [M] CVE-2020-13645

## Summary
Severity: Medium
Advisory: CVE-2020-13645
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:N)
Published: 2020-05-28
Source: https://osv.dev/vulnerability/CVE-2020-13645
Type: osv

## Details
In GNOME glib-networking through 2.64.2, the implementation of GTlsClientConnection skips hostname verification of the server's TLS certificate if the application fails to specify the expected server identity. This is in contrast to its intended documented behavior, to fail the certificate verification. Applications that fail to provide the server identity, including Balsa before 2.5.11 and 2.6.x before 2.6.1, accept a TLS certificate if the certificate is valid for any host.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/HLEX2IP62SU6WJ4SK3U766XGLQK3J62O/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/LRCUM22YEWWKNMN2BP5LTVDM5P4VWIXS/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/TQEQJQ4XFMFCFJTEXKL2ZO3UELBPCKSK/
- https://security.gentoo.org/glsa/202007-50
- https://security.netapp.com/advisory/ntap-20200608-0004/
- https://usn.ubuntu.com/4405-1/
- https://gitlab.gnome.org/GNOME/balsa/-/issues/34
- https://gitlab.gnome.org/GNOME/glib-networking/-/issues/135
