# [C] netaddr before 1.5.3 and 2.0.4 has Incorrect Default Permissions

## Summary
Severity: Critical
Advisory: GHSA-49pj-69vf-c689
CVE: CVE-2019-17383
CWE: CWE-276
Ecosystem: RubyGems
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2019-10-14
Source: https://github.com/advisories/GHSA-49pj-69vf-c689
Type: github-advisory

## Affected
- RubyGems: `netaddr` — affected >=2.0.0 <2.0.4
- RubyGems: `netaddr` — affected >=0 <1.5.3

## Details
The netaddr gem before 1.5.3 and 2.0.4 for Ruby has misconfigured file permissions, such that a gem install may result in 0777 permissions in the target filesystem.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-17383
- https://github.com/dspinhirne/netaddr-rb/issues/29
- https://github.com/dspinhirne/netaddr-rb/pull/20
- https://github.com/dspinhirne/netaddr-rb/commit/3aac46c00a36e71905eaa619cb94d45bff6e3b51
- https://github.com/dspinhirne/netaddr-rb/commit/c7a7de39b7e1126aef11821f98970db18582948b
- https://github.com/dspinhirne/netaddr-rb
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/netaddr/CVE-2019-17383.yml
- https://rubygems.org/gems/netaddr/versions
