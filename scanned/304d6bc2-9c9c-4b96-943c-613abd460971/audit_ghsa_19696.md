# [C] Camaleon CMS Vulnerable to Privilege Escalation through a Mass Assignment

## Summary
Severity: Critical
Advisory: GHSA-rp28-mvq3-wf8j
CVE: CVE-2025-2304
CWE: CWE-915
Ecosystem: RubyGems
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:H/SC:H/SI:H/SA:H (CVSS_V4)
Published: 2025-03-14
Source: https://github.com/advisories/GHSA-rp28-mvq3-wf8j
Type: github-advisory

## Affected
- RubyGems: `camaleon_cms` — affected >=0 <2.9.1

## Details
A Privilege Escalation through a Mass Assignment exists in Camaleon CMS

When a user wishes to change his password, the 'updated_ajax' method of the UsersController is called. The vulnerability stems from the use of the dangerous permit! method, which allows all parameters to pass through without any filtering.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-2304
- https://github.com/owen2345/camaleon-cms/pull/1109
- https://github.com/owen2345/camaleon-cms/commit/179fd6b1ecf258d3e214aebfa87ac4a322ea4db4
- https://github.com/owen2345/camaleon-cms
- https://github.com/owen2345/camaleon-cms/releases/tag/2.9.1
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/camaleon_cms/CVE-2025-2304.yml
- https://www.tenable.com/security/research/tra-2025-09
