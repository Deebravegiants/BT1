# [M] SMTP Smuggling in Postal

## Summary
Severity: Medium
Advisory: CVE-2024-27938
Aliases: GHSA-j42r-6c99-hqf2
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N)
Published: 2024-03-11
Source: https://osv.dev/vulnerability/CVE-2024-27938
Type: osv

## Details
Postal is an open source SMTP server. Postal versions less than 3.0.0 are vulnerable to SMTP Smuggling attacks which may allow incoming e-mails to be spoofed. This, in conjunction with a cooperative outgoing SMTP service, would allow for an incoming e-mail to be received by Postal addressed from a server that a user has 'authorised' to send mail on their behalf but were not the genuine author of the e-mail. Postal is not affected for sending outgoing e-mails as email is re-encoded with `<CR><LF>` line endings when transmitted over SMTP. This issue has been addressed and users should upgrade to Postal v3.0.0 or higher. Once upgraded, Postal will only accept End of DATA sequences which are explicitly `<CR><LF>.<CR><LF>`. If a non-compliant sequence is detected it will be logged to the SMTP server log. There are no workarounds for this issue.

## References
- https://www.postfix.org/smtp-smuggling.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/27xxx/CVE-2024-27938.json
- https://github.com/postalserver/postal/security/advisories/GHSA-j42r-6c99-hqf2
- https://nvd.nist.gov/vuln/detail/CVE-2024-27938
- https://github.com/postalserver/postal/commit/0140dc4
- https://sec-consult.com/blog/detail/smtp-smuggling-spoofing-e-mails-worldwide
