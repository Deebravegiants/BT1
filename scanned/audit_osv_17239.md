# [H] CVE-2020-13962

## Summary
Severity: High
Advisory: CVE-2020-13962
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2020-06-09
Source: https://osv.dev/vulnerability/CVE-2020-13962
Type: osv

## Details
Qt 5.12.2 through 5.14.2, as used in unofficial builds of Mumble 1.3.0 and other products, mishandles OpenSSL's error queue, which can cause a denial of service to QSslSocket users. Because errors leak in unrelated TLS sessions, an unrelated session may be disconnected when any handshake fails. (Mumble 1.3.1 is not affected, regardless of the Qt version.)

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/4X6EDPIIAQPVP2CHL2CHDHJ25EECA7UE/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/UQJDBZUYMMF4R5QQKD2HTIKQU2NSKO63/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/V3IZY7LKJ6NAXQDFYFR4S7L5BBHYK53K/
- http://lists.opensuse.org/opensuse-security-announce/2020-09/msg00004.html
- https://security.gentoo.org/glsa/202007-18
- https://bugreports.qt.io/browse/QTBUG-83450
- https://github.com/mumble-voip/mumble/issues/3679
- https://github.com/mumble-voip/mumble/pull/4032
