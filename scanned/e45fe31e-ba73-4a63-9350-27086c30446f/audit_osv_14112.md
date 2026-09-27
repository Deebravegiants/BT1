# [H] CVE-2018-7284

## Summary
Severity: High
Advisory: CVE-2018-7284
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2018-02-22
Source: https://osv.dev/vulnerability/CVE-2018-7284
Type: osv

## Details
A Buffer Overflow issue was discovered in Asterisk through 13.19.1, 14.x through 14.7.5, and 15.x through 15.2.1, and Certified Asterisk through 13.18-cert2. When processing a SUBSCRIBE request, the res_pjsip_pubsub module stores the accepted formats present in the Accept headers of the request. This code did not limit the number of headers it processed, despite having a fixed limit of 32. If more than 32 Accept headers were present, the code would write outside of its memory and cause a crash.

## References
- http://www.securityfocus.com/bid/103151
- http://www.securitytracker.com/id/1040416
- https://www.debian.org/security/2018/dsa-4320
- http://downloads.asterisk.org/pub/security/AST-2018-004.html
- https://www.exploit-db.com/exploits/44184/
