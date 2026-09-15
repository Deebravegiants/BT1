# [H] CVE-2019-11729

## Summary
Severity: High
Advisory: CVE-2019-11729
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2019-07-23
Source: https://osv.dev/vulnerability/CVE-2019-11729
Type: osv

## Details
Empty or malformed p256-ECDH public keys may trigger a segmentation fault due values being improperly sanitized before being copied into memory and used. This vulnerability affects Firefox ESR < 60.8, Firefox < 68, and Thunderbird < 60.8.

## References
- http://lists.opensuse.org/opensuse-security-announce/2019-07/msg00058.html
- http://lists.opensuse.org/opensuse-security-announce/2019-10/msg00009.html
- http://lists.opensuse.org/opensuse-security-announce/2019-07/msg00055.html
- http://lists.opensuse.org/opensuse-security-announce/2019-08/msg00073.html
- http://lists.opensuse.org/opensuse-security-announce/2019-10/msg00010.html
- https://lists.debian.org/debian-lts-announce/2020/09/msg00029.html
- https://security.gentoo.org/glsa/201908-12
- https://security.gentoo.org/glsa/201908-20
- https://www.mozilla.org/security/advisories/mfsa2019-21/
- https://www.mozilla.org/security/advisories/mfsa2019-23/
- https://access.redhat.com/errata/RHSA-2019:1951
- https://access.redhat.com/errata/RHSA-2019:4190
- https://www.mozilla.org/security/advisories/mfsa2019-22/
- https://bugzilla.mozilla.org/show_bug.cgi?id=1515342
