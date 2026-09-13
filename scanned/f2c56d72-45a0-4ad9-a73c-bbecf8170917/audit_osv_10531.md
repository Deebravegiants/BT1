# [C] CVE-2017-16872

## Summary
Severity: Critical
Advisory: CVE-2017-16872
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-11-17
Source: https://osv.dev/vulnerability/CVE-2017-16872
Type: osv

## Details
An issue was discovered in Teluu pjproject (pjlib and pjlib-util) in PJSIP before 2.7.1. Parsing the numeric header fields in a SIP message (like cseq, ttl, port, etc.) all had the potential to overflow, either causing unintended values to be captured or, if the values were subsequently converted back to strings, a buffer overrun. This will lead to a potential exploit using carefully crafted invalid values.

## References
- https://trac.pjsip.org/repos/milestone/release-2.7.1
- https://trac.pjsip.org/repos/ticket/2056
- https://www.debian.org/security/2018/dsa-4170
