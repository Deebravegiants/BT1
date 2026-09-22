# [C] Consul gem insufficient authentication check - Multiple powers in one controller are not always checked correctly

## Summary
Severity: Critical
Advisory: GHSA-8jhx-9gf4-hhf5
CVE: CVE-2019-16377
CWE: CWE-284
Ecosystem: RubyGems
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2019-09-27
Source: https://github.com/advisories/GHSA-8jhx-9gf4-hhf5
Type: github-advisory

## Affected
- RubyGems: `consul` — affected >=0 <1.0.3

## Details
With the consul ruby gem before 1.0.3, if a controller checks multiple powers  using `:if` or `:except` conditions, these conditions are erroneously applied to all power checks in that controller. This can lead to skipped power checks and hence unauthenticated access to certain controller actions.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-16377
- https://github.com/makandra/consul/issues/49
- https://github.com/makandra/consul
- https://github.com/rubysec/ruby-advisory-db/blob/c26fbc13435b8be448ad59131428538049d165e4/gems/consul/CVE-2019-16377.yml
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/consul/CVE-2019-16377.yml
- https://rubygems.org/gems/consul
