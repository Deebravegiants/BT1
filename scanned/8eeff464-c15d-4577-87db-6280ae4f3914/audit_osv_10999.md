# [M] CVE-2017-5592

## Summary
Severity: Medium
Advisory: CVE-2017-5592
CVSS: 5.9 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:H/A:N)
Published: 2017-02-09
Source: https://osv.dev/vulnerability/CVE-2017-5592
Type: osv

## Details
An incorrect implementation of "XEP-0280: Message Carbons" in multiple XMPP clients allows a remote attacker to impersonate any user, including contacts, in the vulnerable application's display. This allows for various kinds of social engineering attacks. This CVE is for profanity (0.4.7 - 0.5.0).

## References
- http://www.securityfocus.com/bid/96173
- https://github.com/boothj5/profanity/commit/8e75437a7e43d4c55e861691f74892e666e29b0b
- http://openwall.com/lists/oss-security/2017/02/09/29
- https://rt-solutions.de/en/2017/02/CVE-2017-5589_xmpp_carbons/
- https://rt-solutions.de/wp-content/uploads/2017/02/CVE-2017-5589_xmpp_carbons.pdf
