# [H] CVE-2021-26717

## Summary
Severity: High
Advisory: CVE-2021-26717
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2021-02-18
Source: https://osv.dev/vulnerability/CVE-2021-26717
Type: osv

## Details
An issue was discovered in Sangoma Asterisk 16.x before 16.16.1, 17.x before 17.9.2, and 18.x before 18.2.1 and Certified Asterisk before 16.8-cert6. When re-negotiating for T.38, if the initial remote response was delayed just enough, Asterisk would send both audio and T.38 in the SDP. If this happened, and the remote responded with a declined T.38 stream, then Asterisk would crash.

## References
- http://packetstormsecurity.com/files/161471/Asterisk-Project-Security-Advisory-AST-2021-002.html
- https://downloads.asterisk.org/pub/security/
- https://downloads.asterisk.org/pub/security/AST-2021-002.html
- http://seclists.org/fulldisclosure/2021/Feb/58
- https://issues.asterisk.org/jira/browse/ASTERISK-29203
