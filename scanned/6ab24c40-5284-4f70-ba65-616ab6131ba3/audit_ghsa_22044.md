# [C] RubyGem openshift-origin-controller is vulnerable to command injection

## Summary
Severity: Critical
Advisory: GHSA-77xq-7c6p-6xp6
CVE: CVE-2013-2095
CWE: CWE-74
Ecosystem: RubyGems
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-05
Source: https://github.com/advisories/GHSA-77xq-7c6p-6xp6
Type: github-advisory

## Affected
- RubyGems: `openshift-origin-controller` — affected >=0

## Details
rubygem-openshift-origin-controller: API can be used to create applications via cartridge_cache.rb URI.prase() to perform command injection

## References
- https://nvd.nist.gov/vuln/detail/CVE-2013-2095
- https://access.redhat.com/security/cve/cve-2013-2095
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2013-2095
- https://github.com/openshift/origin-server
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/openshift-origin-controller/CVE-2013-2095.yml
