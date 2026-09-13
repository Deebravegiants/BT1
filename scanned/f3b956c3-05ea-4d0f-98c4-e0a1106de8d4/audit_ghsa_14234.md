# [H] Fluent Fluentd and Fluent-ui use default password

## Summary
Severity: High
Advisory: GHSA-wrxf-x8rm-6ggg
CVE: CVE-2020-21514
CWE: CWE-276
Ecosystem: RubyGems
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2023-04-04
Source: https://github.com/advisories/GHSA-wrxf-x8rm-6ggg
Type: github-advisory

## Affected
- RubyGems: `fluentd-ui` — affected >=0

## Details
An issue was discovered in Fluent-ui v.1.2.2 allows attackers to gain escalated privileges and execute arbitrary code due to a default password.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-21514
- https://github.com/fluent/fluentd-ui/issues/295
- https://github.com/fluent/fluentd/issues/2722
- https://github.com/fluent/fluentd-ui
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/fluentd-ui/CVE-2020-21514.yml
