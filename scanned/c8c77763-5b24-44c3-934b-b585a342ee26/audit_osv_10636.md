# [H] CVE-2017-17850

## Summary
Severity: High
Advisory: CVE-2017-17850
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-12-27
Source: https://osv.dev/vulnerability/CVE-2017-17850
Type: osv

## Details
An issue was discovered in Asterisk 13.18.4 and older, 14.7.4 and older, 15.1.4 and older, and 13.18-cert1 and older. A select set of SIP messages create a dialog in Asterisk. Those SIP messages must contain a contact header. For those messages, if the header was not present and the PJSIP channel driver was used, Asterisk would crash. The severity of this vulnerability is somewhat mitigated if authentication is enabled. If authentication is enabled, a user would have to first be authorized before reaching the crash point.

## References
- http://downloads.asterisk.org/pub/security/AST-2017-014.html
- http://www.securitytracker.com/id/1040056
- https://security.gentoo.org/glsa/201811-11
- https://issues.asterisk.org/jira/browse/ASTERISK-27480
