# [M] Fat Free CRM vulnerable to Cross-site Scripting

## Summary
Severity: Medium
Advisory: GHSA-j5rj-g695-342r
CVE: CVE-2018-1000842
CWE: CWE-79
Ecosystem: RubyGems
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2018-12-20
Source: https://github.com/advisories/GHSA-j5rj-g695-342r
Type: github-advisory

## Affected
- RubyGems: `fat_free_crm` — affected >=0 <0.14.2
- RubyGems: `fat_free_crm` — affected >=0.15.0 <0.15.2
- RubyGems: `fat_free_crm` — affected >=0.16.0 <0.16.4
- RubyGems: `fat_free_crm` — affected >=0.17.0 <0.17.3
- RubyGems: `fat_free_crm` — affected >=0.18.0 <0.18.1

## Details
FatFreeCRM version `<=0.14.1`, `>=0.15.0 <=0.15.1`, `>=0.16.0 <=0.16.3`, `>=0.17.0 <=0.17.2`, and `==0.18.0` contains a Cross Site Scripting (XSS) vulnerability in [commit 6d60bc8ed010c4eda05d6645c64849f415f68d65](https://github.com/asteinhauser/fat_free_crm/commit/306f940b26ccf3f406665f07bece1229a7a5dcfa) that can result in Javascript execution. This attack appears to be exploitable via Content with Javascript payload will be executed on end user browsers when they visit the page. This vulnerability appears to have been fixed in 0.18.1, 0.17.3, 0.16.4, 0.15.2, and 0.14.2.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-1000842
- https://github.com/asteinhauser/fat_free_crm/issues/1
- https://github.com/asteinhauser/fat_free_crm/commit/306f940b26ccf3f406665f07bece1229a7a5dcfa
- https://github.com/asteinhauser/fat_free_crm
- https://github.com/fatfreecrm/fat_free_crm/wiki/XSS-Vulnerability-%282018-10-27%29
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/fat_free_crm/CVE-2018-1000842.yml
- https://groups.google.com/forum/#!topic/fat-free-crm-users/TxsdZXSe7Jc
