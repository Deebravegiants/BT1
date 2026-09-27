# [M] CVE-2019-15297

## Summary
Severity: Medium
Advisory: CVE-2019-15297
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2019-09-09
Source: https://osv.dev/vulnerability/CVE-2019-15297
Type: osv

## Details
res_pjsip_t38 in Sangoma Asterisk 15.x before 15.7.4 and 16.x before 16.5.1 allows an attacker to trigger a crash by sending a declined stream in a response to a T.38 re-invite initiated by Asterisk. The crash occurs because of a NULL session media object dereference.

## References
- http://packetstormsecurity.com/files/161671/Asterisk-Project-Security-Advisory-AST-2021-006.html
- http://seclists.org/fulldisclosure/2021/Mar/5
- http://downloads.asterisk.org/pub/security/AST-2019-004.html
- http://packetstormsecurity.com/files/154371/Asterisk-Project-Security-Advisory-AST-2019-004.html
