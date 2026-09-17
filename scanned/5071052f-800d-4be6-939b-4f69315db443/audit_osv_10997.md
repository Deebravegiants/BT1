# [M] CVE-2017-5589

## Summary
Severity: Medium
Advisory: CVE-2017-5589
CVSS: 5.9 (CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:H/A:N)
Published: 2017-02-09
Source: https://osv.dev/vulnerability/CVE-2017-5589
Type: osv

## Details
An incorrect implementation of "XEP-0280: Message Carbons" in multiple XMPP clients allows a remote attacker to impersonate any user, including contacts, in the vulnerable application's display. This allows for various kinds of social engineering attacks. This CVE is for yaxim and Bruno (0.8.6 - 0.8.8; Android).

## References
- http://www.securityfocus.com/bid/96170
- https://github.com/ge0rg/yaxim/commit/65a38dc77545d9568732189e86089390f0ceaf9f
- http://openwall.com/lists/oss-security/2017/02/09/29
- https://rt-solutions.de/en/2017/02/CVE-2017-5589_xmpp_carbons/
- https://rt-solutions.de/wp-content/uploads/2017/02/CVE-2017-5589_xmpp_carbons.pdf
