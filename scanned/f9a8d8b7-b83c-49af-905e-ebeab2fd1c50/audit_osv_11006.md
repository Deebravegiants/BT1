# [M] CVE-2017-5603

## Summary
Severity: Medium
Advisory: CVE-2017-5603
CVSS: 5.9 (CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:H/A:N)
Published: 2017-02-09
Source: https://osv.dev/vulnerability/CVE-2017-5603
Type: osv

## Details
An incorrect implementation of "XEP-0280: Message Carbons" in multiple XMPP clients allows a remote attacker to impersonate any user, including contacts, in the vulnerable application's display. This allows for various kinds of social engineering attacks. This CVE is for Jitsi 2.5.5061 - 2.9.5544.

## References
- http://www.securityfocus.com/bid/96174
- https://github.com/jitsi/jitsi/commit/7d66da61b316c9480b63000f831b6de723b87315
- http://openwall.com/lists/oss-security/2017/02/09/29
- https://rt-solutions.de/en/2017/02/CVE-2017-5589_xmpp_carbons/
- https://rt-solutions.de/wp-content/uploads/2017/02/CVE-2017-5589_xmpp_carbons.pdf
