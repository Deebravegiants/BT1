# [C] PDFKit vulnerable to Command Injection

## Summary
Severity: Critical
Advisory: GHSA-rhwx-hjx2-x4qr
CVE: CVE-2022-25765
CWE: CWE-77
Ecosystem: RubyGems
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-09-10
Source: https://github.com/advisories/GHSA-rhwx-hjx2-x4qr
Type: github-advisory

## Affected
- RubyGems: `pdfkit` — affected >=0 <0.8.7.2

## Details
The package pdfkit is vulnerable to Command Injection where the URL is not properly sanitized.

Note: This issue was patched in 0.8.7.2, but the patch was discovered to be ineffective. The updated patch version is 0.8.7.2.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-25765
- https://github.com/pdfkit/pdfkit/issues/517
- https://github.com/pdfkit/pdfkit/pull/519
- https://github.com/pdfkit/pdfkit
- https://github.com/pdfkit/pdfkit/blob/46cdf53ec540da1a1a2e4da979e3e5fe2f92a257/lib/pdfkit/pdfkit.rb#L55-L58
- https://github.com/pdfkit/pdfkit/blob/46cdf53ec540da1a1a2e4da979e3e5fe2f92a257/lib/pdfkit/pdfkit.rb%23L55-L58
- https://github.com/pdfkit/pdfkit/blob/master/lib/pdfkit/source.rb%23L44-L50
- https://github.com/pdfkit/pdfkit/releases/tag/v0.8.7
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/pdfkit/CVE-2022-25765.yml
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/C36GAV3TKM3JXV6UVMLMTTDRCPKSNETQ
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/ESWB6SX7HYWQ54UGBGQOZ7G24O6RAOKD
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/JFB2BFKH5SUGRKXMY6PWRQNGKZML7GDT
- https://security.snyk.io/vuln/SNYK-RUBY-PDFKIT-2869795
- http://packetstormsecurity.com/files/171746/pdfkit-0.8.7.2-Command-Injection.html
