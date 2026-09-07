# [M] Cross Site Scripting (XSS) vulnerability in easymon

## Summary
Severity: Medium
Advisory: GHSA-c289-47qf-rvrr
CVE: CVE-2018-1000855
CWE: CWE-79
Ecosystem: RubyGems
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2018-12-21
Source: https://github.com/advisories/GHSA-c289-47qf-rvrr
Type: github-advisory

## Affected
- RubyGems: `easymon` — affected >=0 <1.4.1

## Details
easymon version 1.4 and earlier contains a Cross Site Scripting (XSS) vulnerability in Endpoint where monitoring is mounted that can result in Reflected XSS that affects Firefox. Can be used to steal cookies, depending on the cookie settings.. This attack appear to be exploitable via The victim must click on a crafted URL that contains the XSS payload. This vulnerability appears to have been fixed in 1.4.1 and later.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-1000855
- https://github.com/basecamp/easymon/issues/26
- https://github.com/basecamp/easymon/pull/25
- https://github.com/basecamp/easymon
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/easymon/CVE-2018-1000855.yml
