# [M] Fat Free CRM Cross-Site Request Forgery vulnerability

## Summary
Severity: Medium
Advisory: GHSA-wx7c-8j35-mpg8
CVE: CVE-2015-1585
CWE: CWE-352
Ecosystem: RubyGems
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-wx7c-8j35-mpg8
Type: github-advisory

## Affected
- RubyGems: `fat_free_crm` — affected >=0 <0.13.6

## Details
Fat Free CRM before 0.13.6 allows remote attackers to conduct cross-site request forgery (CSRF) attacks via a request without the authenticity_token, as demonstrated by a crafted HTML page that creates a new administrator account.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2015-1585
- https://github.com/fatfreecrm/fat_free_crm/commit/86fd7f98c9583fd36384987282d1c086fdcecd7c
- https://exchange.xforce.ibmcloud.com/vulnerabilities/100925
- https://github.com/fatfreecrm/fat_free_crm
- https://github.com/fatfreecrm/fat_free_crm/wiki/CSRF-Vulnerability-%28CVE-2015-1585%29
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/fat_free_crm/CVE-2015-1585.yml
- http://packetstormsecurity.com/files/130410/Fat-Free-CRM-0.13.5-Cross-Site-Request-Forgery.html
