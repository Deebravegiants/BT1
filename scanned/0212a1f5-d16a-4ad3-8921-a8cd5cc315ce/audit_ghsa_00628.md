# [M] delayed_job_web Cross-site Scripting vulnerability

## Summary
Severity: Medium
Advisory: GHSA-w7q9-xr2x-wh7x
CVE: CVE-2017-12097
CWE: CWE-79
Ecosystem: RubyGems
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2018-03-05
Source: https://github.com/advisories/GHSA-w7q9-xr2x-wh7x
Type: github-advisory

## Affected
- RubyGems: `delayed_job_web` — affected >=1.2.9 <1.4.2

## Details
An exploitable cross site scripting (XSS) vulnerability exists in the filter functionality of the delayed_job_web rails gem versions 1.2.9 before 1.4.2. A specially crafted URL can cause an XSS flaw resulting in an attacker being able to execute arbitrary javascript on the victim's browser. An attacker can phish an authenticated user to trigger this vulnerability.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-12097
- https://github.com/ejschmitt/delayed_job_web/commit/6bcb10e61ea2b9a44ffa16be8536dff46ad51449
- https://github.com/ejschmitt/delayed_job_web
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/delayed_job_web/CVE-2017-12097.yml
- https://rubygems.org/gems/delayed_job_web/versions/1.4
- https://web.archive.org/web/20200227132840/http://www.securityfocus.com/bid/102484
- https://www.talosintelligence.com/vulnerability_reports/TALOS-2017-0449
