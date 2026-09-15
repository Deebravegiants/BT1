# [H] CVE-2017-11655

## Summary
Severity: High
Advisory: CVE-2017-11655
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-07-26
Source: https://osv.dev/vulnerability/CVE-2017-11655
Type: osv

## Details
A memory leak was found in the way SIPcrack 0.2 handled processing of SIP traffic, because a lines array was mismanaged. A remote attacker could potentially use this flaw to crash long-running sipdump network sniffing sessions.

## References
- http://www.securityfocus.com/bid/100024
- http://openwall.com/lists/oss-security/2017/07/26/1
