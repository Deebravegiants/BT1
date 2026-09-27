# [M] Fat Free CRM allows remote attackers to obtain sensitive information via a direct request

## Summary
Severity: Medium
Advisory: GHSA-4xq9-vw89-p5cx
CVE: CVE-2013-7224
CWE: CWE-200
Ecosystem: RubyGems
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-4xq9-vw89-p5cx
Type: github-advisory

## Affected
- RubyGems: `fat_free_crm` — affected >=0 <0.12.1

## Details
Fat Free CRM before 0.12.1 does not restrict JSON serialization, which allows remote attackers to obtain sensitive information via a direct request, as demonstrated by a request for `users/1.json`.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2013-7224
- https://github.com/fatfreecrm/fat_free_crm/issues/300
- https://github.com/fatfreecrm/fat_free_crm/commit/cf26a04b356ad2161c4c6160260eb870a3de5328
- https://github.com/fatfreecrm/fat_free_crm
- https://github.com/fatfreecrm/fat_free_crm/wiki/Fixing-security-vulnerabilities-%2827th-Dec-2013%29
- http://openwall.com/lists/oss-security/2013/12/28/2
- http://seclists.org/fulldisclosure/2013/Dec/199
