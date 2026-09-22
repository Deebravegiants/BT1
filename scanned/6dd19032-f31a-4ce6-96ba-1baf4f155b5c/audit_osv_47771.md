# [M] CVE-2017-11654

## Summary
Severity: Medium
Advisory: CVE-2017-11654
CVSS: 5.9 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-07-26
Source: https://osv.dev/vulnerability/CVE-2017-11654
Type: osv

## Details
An out-of-bounds read and write flaw was found in the way SIPcrack 0.2 processed SIP traffic, because 0x00 termination of a payload array was mishandled. A remote attacker could potentially use this flaw to crash the sipdump process by generating specially crafted SIP traffic.

## References
- http://www.securityfocus.com/bid/100023
- http://openwall.com/lists/oss-security/2017/07/26/1
