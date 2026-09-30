# [H] CVE-2016-9937

## Summary
Severity: High
Advisory: CVE-2016-9937
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2016-12-12
Source: https://osv.dev/vulnerability/CVE-2016-9937
Type: osv

## Details
An issue was discovered in Asterisk Open Source 13.12.x and 13.13.x before 13.13.1 and 14.x before 14.2.1. If an SDP offer or answer is received with the Opus codec and with the format parameters separated using a space the code responsible for parsing will recursively call itself until it crashes. This occurs as the code does not properly handle spaces separating the parameters. This does NOT require the endpoint to have Opus configured in Asterisk. This also does not require the endpoint to be authenticated. If guest is enabled for chan_sip or anonymous in chan_pjsip an SDP offer or answer is still processed and the crash occurs.

## References
- http://www.securitytracker.com/id/1037407
- http://www.securityfocus.com/bid/94792
- http://downloads.asterisk.org/pub/security/AST-2016-008-13.diff
- http://downloads.asterisk.org/pub/security/AST-2016-008-14.diff
- http://downloads.asterisk.org/pub/security/AST-2016-008.html
- https://issues.asterisk.org/jira/browse/ASTERISK-26579
