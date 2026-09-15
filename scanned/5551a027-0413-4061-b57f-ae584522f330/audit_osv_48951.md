# [C] CVE-2018-18505

## Summary
Severity: Critical
Advisory: CVE-2018-18505
CVSS: 10.0 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:H)
Published: 2019-02-05
Source: https://osv.dev/vulnerability/CVE-2018-18505
Type: osv

## Details
An earlier fix for an Inter-process Communication (IPC) vulnerability, CVE-2011-3079, added authentication to communication between IPC endpoints and server parents during IPC process creation. This authentication is insufficient for channels created after the IPC process is started, leading to the authentication not being correctly applied to later channels. This could allow for a sandbox escape through IPC channels due to lack of message validation in the listener process. This vulnerability affects Thunderbird < 60.5, Firefox ESR < 60.5, and Firefox < 65.

## References
- http://lists.opensuse.org/opensuse-security-announce/2019-07/msg00021.html
- http://www.securityfocus.com/bid/106781
- https://access.redhat.com/errata/RHSA-2019:0269
- https://lists.debian.org/debian-lts-announce/2019/02/msg00024.html
- https://access.redhat.com/errata/RHSA-2019:0219
- https://access.redhat.com/errata/RHSA-2019:0270
- https://security.gentoo.org/glsa/201903-04
- https://usn.ubuntu.com/3874-1/
- https://usn.ubuntu.com/3897-1/
- https://www.debian.org/security/2019/dsa-4392
- https://www.mozilla.org/security/advisories/mfsa2019-01/
- https://access.redhat.com/errata/RHSA-2019:0218
- https://lists.debian.org/debian-lts-announce/2019/01/msg00025.html
- https://security.gentoo.org/glsa/201904-07
- https://www.debian.org/security/2019/dsa-4376
- https://www.mozilla.org/security/advisories/mfsa2019-02/
- https://www.mozilla.org/security/advisories/mfsa2019-03/
- https://bugzilla.mozilla.org/show_bug.cgi?id=1087565
