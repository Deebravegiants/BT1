# [M] katello Improper Privilege Management vulnerability

## Summary
Severity: Medium
Advisory: GHSA-cpv6-pfq6-j2v7
CVE: CVE-2017-2662
CWE: CWE-269
Ecosystem: RubyGems
CVSS: CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-cpv6-pfq6-j2v7
Type: github-advisory

## Affected
- RubyGems: `katello` — affected >=0 <3.17.0.rc1

## Details
A flaw was found in Foreman's katello plugin version 3.4.5. After setting a new role to allow restricted access on a repository with a filter (filter set on the Product Name), the filter is not respected when the actions are done via hammer using the repository id.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-2662
- https://github.com/Katello/katello/pull/8772
- https://github.com/Katello/katello/commit/853260e3e9f94179d5881199e7885d1c08e600f6
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2017-2662
- https://github.com/Katello/katello
- https://projects.theforeman.org/issues/18838
