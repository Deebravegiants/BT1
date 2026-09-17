# [M] CVE-2021-31878

## Summary
Severity: Medium
Advisory: CVE-2021-31878
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2021-07-30
Source: https://osv.dev/vulnerability/CVE-2021-31878
Type: osv

## Details
An issue was discovered in PJSIP in Asterisk before 16.19.1 and before 18.5.1. To exploit, a re-INVITE without SDP must be received after Asterisk has sent a BYE request.

## References
- https://issues.asterisk.org/jira/browse/ASTERISK-29381
- http://downloads.asterisk.org/pub/security/AST-2021-007.html
- http://packetstormsecurity.com/files/163638/Asterisk-Project-Security-Advisory-AST-2021-007.html
- http://seclists.org/fulldisclosure/2021/Jul/48
- https://downloads.digium.com/pub/security/AST-2021-007.html
