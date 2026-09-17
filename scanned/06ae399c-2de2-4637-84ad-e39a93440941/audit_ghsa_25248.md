# [M] XMPP Clients User Impersonation Vulnerability in Movim Moxl

## Summary
Severity: Medium
Advisory: GHSA-hq38-v658-g3wp
CVE: CVE-2017-5605
CWE: CWE-20
Ecosystem: Packagist
CVSS: CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-hq38-v658-g3wp
Type: github-advisory

## Affected
- Packagist: `movim/moxl` — affected >=0.8

## Details
An incorrect implementation of "XEP-0280: Message Carbons" in multiple XMPP clients allows a remote attacker to impersonate any user, including contacts, in the vulnerable application's display. This allows for various kinds of social engineering attacks. This CVE is for Movim 0.8 - 0.10.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-5605
- https://github.com/movim/moxl/commit/838b0a42efc3b67cc17d63e25ae1d0ea849cd89b
- https://rt-solutions.de/wp-content/uploads/2017/02/CVE-2017-5589_xmpp_carbons.pdf
- https://web.archive.org/web/20170301232720/https://rt-solutions.de/en/2017/02/CVE-2017-5589_xmpp_carbons
- https://web.archive.org/web/20210123225200/https://www.securityfocus.com/bid/96177
- http://openwall.com/lists/oss-security/2017/02/09/29
