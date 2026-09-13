# [C] colorscore Command Injection vulnerability

## Summary
Severity: Critical
Advisory: GHSA-73qw-ww62-m54x
CVE: CVE-2015-7541
CWE: CWE-77
Ecosystem: RubyGems
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2017-10-24
Source: https://github.com/advisories/GHSA-73qw-ww62-m54x
Type: github-advisory

## Affected
- RubyGems: `colorscore` — affected >=0 <0.0.5

## Details
The initialize method in the Histogram class in `lib/colorscore/histogram.rb` in the colorscore gem before 0.0.5 for Ruby allows context-dependent attackers to execute arbitrary code via shell metacharacters in the (1) `image_path`, (2) `colors`, or (3) `depth` variable.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2015-7541
- https://github.com/quadule/colorscore/commit/570b5e854cecddd44d2047c44126aed951b61718
- https://github.com/quadule/colorscore
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/colorscore/CVE-2015-7541.yml
- http://rubysec.com/advisories/CVE-2015-7541
- http://seclists.org/oss-sec/2016/q1/17
- http://www.openwall.com/lists/oss-security/2016/01/05/2
