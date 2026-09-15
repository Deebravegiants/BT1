# [M] apollo_upload_server has Denial of Service vulnerability

## Summary
Severity: Medium
Advisory: GHSA-w6pv-c757-6rgr
CVE: CVE-2021-39880
Ecosystem: RubyGems
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-w6pv-c757-6rgr
Type: github-advisory

## Affected
- RubyGems: `apollo_upload_server` — affected >=0 <2.1.0

## Details
A Denial Of Service vulnerability in the apollo_upload_server Ruby gem in GitLab CE/EE version 11.11 and above allows an attacker to deny access to all users via specially crafted requests to the apollo_upload_server middleware.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-39880
- https://github.com/jetruby/apollo_upload_server-ruby/pull/44
- https://github.com/jetruby/apollo_upload_server-ruby/commit/b0582c1a3e458eee3c994fb38278bd0221f20486
- https://hackerone.com/reports/1181284
- https://github.com/jetruby/apollo_upload_server-ruby
- https://github.com/jetruby/apollo_upload_server-ruby/releases/tag/2.1.0
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/apollo_upload_server/CVE-2021-39880.yml
- https://gitlab.com/gitlab-org/cves/-/blob/master/2021/CVE-2021-39880.json
- https://gitlab.com/gitlab-org/gitlab/-/issues/330561
- https://gitlab.com/gitlab-org/gitlab/-/issues/330561#note_642879964
- https://vuldb.com/?id.183842
