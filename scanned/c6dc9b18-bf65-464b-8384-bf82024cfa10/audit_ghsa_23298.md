# [M] Fat Free CRM has fixed token value

## Summary
Severity: Medium
Advisory: GHSA-g897-cgfc-7q8v
CVE: CVE-2013-7222
CWE: CWE-330
Ecosystem: RubyGems
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-g897-cgfc-7q8v
Type: github-advisory

## Affected
- RubyGems: `fat_free_crm` — affected >=0 <0.12.1

## Details
`config/initializers/secret_token.rb` in Fat Free CRM before 0.12.1 has a fixed `FatFreeCRM::Application.config.secret_token` value, which makes it easier for remote attackers to spoof signed cookies by referring to the key in the source code.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2013-7222
- https://github.com/fatfreecrm/fat_free_crm/issues/300
- https://github.com/fatfreecrm/fat_free_crm/commit/93c182dd4c6f3620b721d2a15ba6a6ecab5669df
- https://github.com/fatfreecrm/fat_free_crm
- https://github.com/fatfreecrm/fat_free_crm/wiki/Fixing-security-vulnerabilities-%2827th-Dec-2013%29
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/fat_free_crm/CVE-2013-7222.yml
- http://openwall.com/lists/oss-security/2013/12/28/2
- http://seclists.org/fulldisclosure/2013/Dec/199
