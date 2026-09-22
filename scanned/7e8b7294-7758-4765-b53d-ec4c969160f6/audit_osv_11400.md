# [H] CVE-2017-7617

## Summary
Severity: High
Advisory: CVE-2017-7617
CVSS: 8.8 (CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-04-10
Source: https://osv.dev/vulnerability/CVE-2017-7617
Type: osv

## Details
Remote code execution can occur in Asterisk Open Source 13.x before 13.14.1 and 14.x before 14.3.1 and Certified Asterisk 13.13 before 13.13-cert3 because of a buffer overflow in a CDR user field, related to X-ClientCode in chan_sip, the CDR dialplan function, and the AMI Monitor action.

## References
- http://www.securityfocus.com/bid/97377
- http://downloads.asterisk.org/pub/security/AST-2017-001.html
- https://bugs.debian.org/859910
