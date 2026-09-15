# [H] CVE-2021-41141

## Summary
Severity: High
Advisory: CVE-2021-41141
Aliases: GHSA-8fmx-hqw7-6gmc
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2022-01-04
Source: https://osv.dev/vulnerability/CVE-2021-41141
Type: osv

## Details
PJSIP is a free and open source multimedia communication library written in the C language implementing standard based protocols such as SIP, SDP, RTP, STUN, TURN, and ICE. In various parts of PJSIP, when error/failure occurs, it is found that the function returns without releasing the currently held locks. This could result in a system deadlock, which cause a denial of service for the users. No release has yet been made which contains the linked fix commit. All versions up to an including 2.11.1 are affected. Users may need to manually apply the patch.

## References
- https://lists.debian.org/debian-lts-announce/2022/03/msg00035.html
- https://security.gentoo.org/glsa/202210-37
- https://github.com/pjsip/pjproject/commit/1aa2c0e0fb60a1b0bf793e0d834073ffe50fb196
- https://github.com/pjsip/pjproject/security/advisories/GHSA-8fmx-hqw7-6gmc
