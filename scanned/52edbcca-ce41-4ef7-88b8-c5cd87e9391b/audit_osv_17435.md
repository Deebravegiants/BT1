# [H] CVE-2020-15166

## Summary
Severity: High
Advisory: CVE-2020-15166
Aliases: GHSA-25wp-cf8g-938m
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2020-09-11
Source: https://osv.dev/vulnerability/CVE-2020-15166
Type: osv

## Details
In ZeroMQ before version 4.3.3, there is a denial-of-service vulnerability. Users with TCP transport public endpoints, even with CURVE/ZAP enabled, are impacted. If a raw TCP socket is opened and connected to an endpoint that is fully configured with CURVE/ZAP, legitimate clients will not be able to exchange any message. Handshakes complete successfully, and messages are delivered to the library, but the server application never receives them. This is patched in version 4.3.3.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/BZ5IMNQXDB52JFBXHFLK4AHVORFELNNG/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/YFW2ZELCCPS4VLU4OSJOH5YL6KFKTFYW/
- https://lists.debian.org/debian-lts-announce/2020/11/msg00017.html
- https://security.gentoo.org/glsa/202009-12
- https://github.com/zeromq/libzmq/pull/3913
- https://github.com/zeromq/libzmq/pull/3973
- https://github.com/zeromq/libzmq/security/advisories/GHSA-25wp-cf8g-938m
