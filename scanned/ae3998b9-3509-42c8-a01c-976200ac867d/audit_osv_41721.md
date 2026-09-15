# [M] Mail: Email address spoofing via malformed RFC 2047 encoded-words

## Summary
Severity: Medium
Advisory: CVE-2026-63435
Aliases: GHSA-mvxr-6m87-mv2q
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N)
Published: 2026-09-01
Source: https://osv.dev/vulnerability/CVE-2026-63435
Type: osv

## Details
Mail is an internet library for Ruby designed to handle email generation, parsing, and sending. Prior to 2.9.1, Mail::Utilities.q_value_decode and Mail::Utilities.b_value_decode used a single String#match and an overly greedy charset capture to decode only the first RFC 2047 encoded-word and mishandle surrounding or subsequent text. A crafted malformed encoded-word in an address display name or local part could cross ? delimiters and make decoded From, To, or Reply-To header values differ from the raw values inspected by a human reviewer or downstream parser, enabling apparent sender or recipient spoofing, phishing, or authorization-check bypass. This issue is fixed in version 2.9.1.

## References
- https://github.com/mikel/mail/releases/tag/2.9.1
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/63xxx/CVE-2026-63435.json
- https://github.com/mikel/mail/security/advisories/GHSA-mvxr-6m87-mv2q
- https://nvd.nist.gov/vuln/detail/CVE-2026-63435
- https://github.com/mikel/mail/commit/f9d59c2e447af42e2c3dec5a56b1bb25c7292859
- https://github.com/mikel/mail/pull/1664
