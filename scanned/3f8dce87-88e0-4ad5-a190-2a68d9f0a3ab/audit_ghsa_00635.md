# [M] rails_admin ruby gem XSS

## Summary
Severity: Medium
Advisory: GHSA-pxr8-w3jq-rcwj
CVE: CVE-2017-12098
CWE: CWE-79
Ecosystem: RubyGems
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2018-03-05
Source: https://github.com/advisories/GHSA-pxr8-w3jq-rcwj
Type: github-advisory

## Affected
- RubyGems: `rails_admin` — affected >=0 <1.3.0

## Details
An exploitable cross site scripting (XSS) vulnerability exists in the add filter functionality of the rails_admin rails gem version 1.2.0. A specially crafted URL can cause an XSS flaw resulting in an attacker being able to execute arbitrary javascript on the victim's browser. An attacker can phish an authenticated user to trigger this vulnerability.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-12098
- https://github.com/advisories/GHSA-pxr8-w3jq-rcwj
- https://github.com/railsadminteam/rails_admin
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/rails_admin/CVE-2017-12098.yml
- https://web.archive.org/web/20210116160904/http://www.securityfocus.com/bid/102486
- https://www.talosintelligence.com/vulnerability_reports/TALOS-2017-0450
