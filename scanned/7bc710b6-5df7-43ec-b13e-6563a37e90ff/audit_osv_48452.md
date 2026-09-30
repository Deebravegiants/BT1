# [H] CVE-2017-7805

## Summary
Severity: High
Advisory: CVE-2017-7805
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2018-06-11
Source: https://osv.dev/vulnerability/CVE-2017-7805
Type: osv

## Details
During TLS 1.2 exchanges, handshake hashes are generated which point to a message buffer. This saved data is used for later messages but in some cases, the handshake transcript can exceed the space available in the current buffer, causing the allocation of a new buffer. This leaves a pointer pointing to the old, freed buffer, resulting in a use-after-free when handshake hashes are then calculated afterwards. This can result in a potentially exploitable crash. This vulnerability affects Firefox < 56, Firefox ESR < 52.4, and Thunderbird < 52.4.

## References
- https://www.debian.org/security/2017/dsa-3998
- https://www.mozilla.org/security/advisories/mfsa2017-21/
- https://lists.debian.org/debian-lts-announce/2017/11/msg00000.html
- https://security.gentoo.org/glsa/201803-14
- https://www.debian.org/security/2017/dsa-4014
- https://www.mozilla.org/security/advisories/mfsa2017-22/
- https://www.mozilla.org/security/advisories/mfsa2017-23/
- http://www.oracle.com/technetwork/security-advisory/cpuoct2018-4428296.html
- http://www.securityfocus.com/bid/101059
- http://www.securitytracker.com/id/1039465
- https://access.redhat.com/errata/RHSA-2017:2832
- https://www.debian.org/security/2017/dsa-3987
- https://bugzilla.mozilla.org/show_bug.cgi?id=1377618
