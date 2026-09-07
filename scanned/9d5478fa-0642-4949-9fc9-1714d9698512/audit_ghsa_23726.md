# [M] Camaleon CMS vulnerable to Stored Cross-site Scripting

## Summary
Severity: Medium
Advisory: GHSA-7f84-9cqf-g4j9
CVE: CVE-2018-18260
CWE: CWE-79
Ecosystem: RubyGems
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-7f84-9cqf-g4j9
Type: github-advisory

## Affected
- RubyGems: `camaleon_cms` — affected 2.4

## Details
In the 2.4 version of Camaleon CMS, Stored XSS has been discovered. The profile image in the User settings section can be run in the update / upload area via `/admin/media/upload?actions=false`.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-18260
- https://github.com/owen2345/camaleon-cms
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/camaleon_cms/CVE-2018-18260.yml
- http://packetstormsecurity.com/files/149772/CAMALEON-CMS-2.4-Cross-Site-Scripting.html
