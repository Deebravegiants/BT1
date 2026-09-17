# [H] CVE-2021-26712

## Summary
Severity: High
Advisory: CVE-2021-26712
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2021-02-18
Source: https://osv.dev/vulnerability/CVE-2021-26712
Type: osv

## Details
Incorrect access controls in res_srtp.c in Sangoma Asterisk 13.38.1, 16.16.0, 17.9.1, and 18.2.0 and Certified Asterisk 16.8-cert5 allow a remote unauthenticated attacker to prematurely terminate secure calls by replaying SRTP packets.

## References
- http://packetstormsecurity.com/files/161473/Asterisk-Project-Security-Advisory-AST-2021-003.html
- http://seclists.org/fulldisclosure/2021/Feb/59
- https://downloads.asterisk.org/pub/security/
- https://downloads.asterisk.org/pub/security/AST-2021-003.html
- https://issues.asterisk.org/jira/browse/ASTERISK-29260
