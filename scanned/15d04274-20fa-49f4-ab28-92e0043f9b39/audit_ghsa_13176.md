# [M] sidekiq Denial of Service vulnerability

## Summary
Severity: Medium
Advisory: GHSA-3qc2-v3hp-6cv8
CVE: CVE-2023-26141
CWE: CWE-345, CWE-400
Ecosystem: RubyGems
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2023-09-14
Source: https://github.com/advisories/GHSA-3qc2-v3hp-6cv8
Type: github-advisory

## Affected
- RubyGems: `sidekiq` — affected >=7.0.0 <7.1.3
- RubyGems: `sidekiq` — affected >=0 <6.5.10

## Details
Versions of the package sidekiq before 7.1.3 and 6.5.10 are vulnerable to Denial of Service (DoS) due to insufficient checks in the dashboard-charts.js file. An attacker can exploit this vulnerability by manipulating the localStorage value which will cause excessive polling requests.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-26141
- https://github.com/sidekiq/sidekiq/commit/62c90d7c5a7d8a378d79909859d87c2e0702bf89
- https://gist.github.com/keeganparr1/1dffd3c017339b7ed5371ed3d81e6b2a
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/sidekiq/CVE-2023-26141.yml
- https://github.com/sidekiq/sidekiq
- https://github.com/sidekiq/sidekiq/blob/6-x/Changes.md#6510
- https://github.com/sidekiq/sidekiq/blob/6-x/web/assets/javascripts/dashboard.js#L6
- https://github.com/sidekiq/sidekiq/blob/6-x/web/assets/javascripts/dashboard.js%23L6
- https://security.snyk.io/vuln/SNYK-RUBY-SIDEKIQ-5885107
