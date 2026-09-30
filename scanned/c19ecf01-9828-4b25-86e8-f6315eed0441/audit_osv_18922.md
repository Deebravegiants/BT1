# [H] CVE-2020-4067

## Summary
Severity: High
Advisory: CVE-2020-4067
Aliases: GHSA-c8r8-8vp5-6gcm
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2020-06-29
Source: https://osv.dev/vulnerability/CVE-2020-4067
Type: osv

## Details
In coturn before version 4.5.1.3, there is an issue whereby STUN/TURN response buffer is not initialized properly. There is a leak of information between different client connections. One client (an attacker) could use their connection to intelligently query coturn to get interesting bytes in the padding bytes from the connection of another client. This has been fixed in 4.5.1.3.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/5G35UBNSRLL6SYRTODYTMBJ65TLQILUM/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/TNJJO77ZLGGFJWNUGP6VDG5HPAC5UDBK/
- http://lists.opensuse.org/opensuse-security-announce/2020-07/msg00010.html
- https://github.com/coturn/coturn/blob/aab60340b201d55c007bcdc853230f47aa2dfdf1/ChangeLog#L15
- https://github.com/coturn/coturn/security/advisories/GHSA-c8r8-8vp5-6gcm
- https://lists.debian.org/debian-lts-announce/2020/07/msg00002.html
- https://usn.ubuntu.com/4415-1/
- https://www.debian.org/security/2020/dsa-4711
- https://github.com/coturn/coturn/issues/583
