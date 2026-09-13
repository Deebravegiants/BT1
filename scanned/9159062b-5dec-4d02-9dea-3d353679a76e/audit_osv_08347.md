# [C] CVE-2016-2385

## Summary
Severity: Critical
Advisory: CVE-2016-2385
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2016-04-11
Source: https://osv.dev/vulnerability/CVE-2016-2385
Type: osv

## Details
Heap-based buffer overflow in the encode_msg function in encode_msg.c in the SEAS module in Kamailio (formerly OpenSER and SER) before 4.3.5 allows remote attackers to cause a denial of service (memory corruption and process crash) or possibly execute arbitrary code via a large SIP packet.

## References
- http://www.kamailio.org/pub/kamailio/4.3.5/ChangeLog
- http://www.securityfocus.com/archive/1/537926/100/0/threaded
- http://www.debian.org/security/2016/dsa-3535
- http://www.debian.org/security/2016/dsa-3537
- http://packetstormsecurity.com/files/136477/Kamailio-4.3.4-Heap-Overflow.html
- https://census-labs.com/news/2016/03/30/kamailio-seas-heap-overflow/
- https://github.com/kamailio/kamailio/commit/f50c9c853e7809810099c970780c30b0765b0643
- https://www.exploit-db.com/exploits/39638/
