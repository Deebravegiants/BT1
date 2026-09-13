# [C] Code injection in pdf_info

## Summary
Severity: Critical
Advisory: GHSA-9fh3-j99m-f4v7
CVE: CVE-2022-36231
CWE: CWE-78, CWE-94
Ecosystem: RubyGems
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2023-02-24
Source: https://github.com/advisories/GHSA-9fh3-j99m-f4v7
Type: github-advisory

## Affected
- RubyGems: `pdf_info` — affected >=0

## Details
pdf_info 0.5.3 is vulnerable to Command Execution. An attacker using a specially crafted payload may execute OS commands by using command chaining because during object initalization there is no validation performed and the user provided path is used.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-36231
- https://github.com/newspaperclub/pdf_info/issues/16
- https://github.com/newspaperclub/pdf_info/pull/15
- https://github.com/affix/CVE-2022-36231
- https://github.com/newspaperclub/pdf_info
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/pdf_info/CVE-2022-36231.yml
- https://rubygems.org/gems/pdf_info
