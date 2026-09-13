# [M] CVE-2021-26906

## Summary
Severity: Medium
Advisory: CVE-2021-26906
CVSS: 5.9 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2021-02-18
Source: https://osv.dev/vulnerability/CVE-2021-26906
Type: osv

## Details
An issue was discovered in res_pjsip_session.c in Digium Asterisk through 13.38.1; 14.x, 15.x, and 16.x through 16.16.0; 17.x through 17.9.1; and 18.x through 18.2.0, and Certified Asterisk through 16.8-cert5. An SDP negotiation vulnerability in PJSIP allows a remote server to potentially crash Asterisk by sending specific SIP responses that cause an SDP negotiation failure.

## References
- http://packetstormsecurity.com/files/161477/Asterisk-Project-Security-Advisory-AST-2021-005.html
- https://downloads.asterisk.org/pub/security/
- https://downloads.asterisk.org/pub/security/AST-2021-005.html
- http://seclists.org/fulldisclosure/2021/Feb/61
- https://issues.asterisk.org/jira/browse/ASTERISK-29196
