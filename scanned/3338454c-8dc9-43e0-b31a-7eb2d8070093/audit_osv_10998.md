# [M] CVE-2017-5590

## Summary
Severity: Medium
Advisory: CVE-2017-5590
CVSS: 5.9 (CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:H/A:N)
Published: 2017-02-09
Source: https://osv.dev/vulnerability/CVE-2017-5590
Type: osv

## Details
An incorrect implementation of "XEP-0280: Message Carbons" in multiple XMPP clients allows a remote attacker to impersonate any user, including contacts, in the vulnerable application's display. This allows for various kinds of social engineering attacks. This CVE is for ChatSecure (3.2.0 - 4.0.0; only iOS) and Zom (all versions up to 1.0.11; only iOS).

## References
- http://www.securityfocus.com/bid/96165
- https://github.com/ChatSecure/ChatSecure-iOS/commit/a340b4bb519227d89f85f2716a10a197a65d4856
- https://github.com/zom/Zom-iOS/commit/880051eaa8ba32d1b257c87a7d8798a93561bfd3
- http://openwall.com/lists/oss-security/2017/02/09/29
- https://rt-solutions.de/en/2017/02/CVE-2017-5589_xmpp_carbons/
- https://rt-solutions.de/wp-content/uploads/2017/02/CVE-2017-5589_xmpp_carbons.pdf
