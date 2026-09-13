# [H] CVE-2017-5335

## Summary
Severity: High
Advisory: CVE-2017-5335
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-03-24
Source: https://osv.dev/vulnerability/CVE-2017-5335
Type: osv

## Details
The stream reading functions in lib/opencdk/read-packet.c in GnuTLS before 3.3.26 and 3.5.x before 3.5.8 allow remote attackers to cause a denial of service (out-of-memory error and crash) via a crafted OpenPGP certificate.

## References
- http://lists.opensuse.org/opensuse-security-announce/2017-02/msg00005.html
- http://rhn.redhat.com/errata/RHSA-2017-0574.html
- http://www.securityfocus.com/bid/95374
- http://www.securitytracker.com/id/1037576
- https://access.redhat.com/errata/RHSA-2017:2292
- https://gnutls.org/security.html#GNUTLS-SA-2017-2
- http://www.openwall.com/lists/oss-security/2017/01/10/7
- http://www.openwall.com/lists/oss-security/2017/01/11/4
- https://bugs.chromium.org/p/oss-fuzz/issues/detail?id=337
- https://gitlab.com/gnutls/gnutls/commit/49be4f7b82eba2363bb8d4090950dad976a77a3a
- https://security.gentoo.org/glsa/201702-04
