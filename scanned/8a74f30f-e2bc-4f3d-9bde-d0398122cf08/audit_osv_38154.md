# [H] Plunk has a CRLF Email Header Injection in raw MIME message construction allows authenticated API user to inject arbitrary email headers

## Summary
Severity: High
Advisory: CVE-2026-34975
Aliases: GHSA-2mvm-rg5v-7hfq
CVSS: 8.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:L/A:N)
Published: 2026-04-06
Source: https://osv.dev/vulnerability/CVE-2026-34975
Type: osv

## Details
Plunk is an open-source email platform built on top of AWS SES. Prior to 0.8.0, a CRLF header injection vulnerability was discovered in SESService.ts, where user-supplied values for from.name, subject, custom header keys/values, and attachment filenames were interpolated directly into raw MIME messages without sanitization. An authenticated API user could inject arbitrary email headers (e.g. Bcc, Reply-To) by embedding carriage return/line feed characters in these fields, enabling silent email forwarding, reply redirection, or sender spoofing. The fix adds input validation at the schema level to reject any of these fields containing \r or \n characters, consistent with the existing validation already applied to the contentId field. This vulnerability is fixed in 0.8.0.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/34xxx/CVE-2026-34975.json
- https://github.com/useplunk/plunk/security/advisories/GHSA-2mvm-rg5v-7hfq
- https://nvd.nist.gov/vuln/detail/CVE-2026-34975
