# [M] Mail Gem CRLF Injection vulnerability

## Summary
Severity: Medium
Advisory: GHSA-q86f-fmqf-qrf6
CVE: CVE-2015-9097
CWE: CWE-93
Ecosystem: RubyGems
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2017-10-24
Source: https://github.com/advisories/GHSA-q86f-fmqf-qrf6
Type: github-advisory

## Affected
- RubyGems: `mail` — affected >=0 <2.5.5

## Details
The mail gem before 2.5.5 for Ruby (aka A Really Ruby Mail Library) is vulnerable to SMTP command injection via CRLF sequences in a RCPT TO or MAIL FROM command, as demonstrated by CRLF sequences immediately before and after a DATA substring.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2015-9097
- https://github.com/rubysec/ruby-advisory-db/issues/215
- https://github.com/mikel/mail/pull/1097
- https://github.com/mikel/mail/commit/72befdc4dab3e6e288ce226a7da2aa474cf5be83
- https://hackerone.com/reports/137631
- https://github.com/advisories/GHSA-q86f-fmqf-qrf6
- https://github.com/mikel/mail
- https://rubysec.com/advisories/mail-OSVDB-131677
- http://openwall.com/lists/oss-security/2015/12/11/3
- http://www.mbsd.jp/Whitepaper/smtpi.pdf
