# [C] CVE-2019-17362

## Summary
Severity: Critical
Advisory: CVE-2019-17362
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:H)
Published: 2019-10-09
Source: https://osv.dev/vulnerability/CVE-2019-17362
Type: osv

## Details
In LibTomCrypt through 1.18.2, the der_decode_utf8_string function (in der_decode_utf8_string.c) does not properly detect certain invalid UTF-8 sequences. This allows context-dependent attackers to cause a denial of service (out-of-bounds read and crash) or read information from other memory locations via carefully crafted DER-encoded data.

## References
- http://lists.opensuse.org/opensuse-security-announce/2019-11/msg00020.html
- http://lists.opensuse.org/opensuse-security-announce/2019-11/msg00041.html
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/47YP5SXQ4RY6KMTK2HI5ZZR244XKRMCZ/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/YU5OMCY3PX54YVI4FMNDEENHDJZJ3RJW/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/47YP5SXQ4RY6KMTK2HI5ZZR244XKRMCZ/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/YU5OMCY3PX54YVI4FMNDEENHDJZJ3RJW/
- https://lists.debian.org/debian-lts-announce/2019/10/msg00010.html
- https://vuldb.com/?id.142995
- https://github.com/libtom/libtomcrypt/pull/508
- https://github.com/libtom/libtomcrypt/issues/507
