# [M] Script Injection in Show In Browser gem

## Summary
Severity: Medium
Advisory: GHSA-9hx9-w2j6-rw76
CVE: CVE-2013-2105
CWE: CWE-59
Ecosystem: RubyGems
Published: 2017-10-24
Source: https://github.com/advisories/GHSA-9hx9-w2j6-rw76
Type: github-advisory

## Affected
- RubyGems: `show_in_browser` — affected 0.0.3

## Details
The Show In Browser (show_in_browser) gem 0.0.3 for Ruby allows local users to inject arbitrary web script or HTML via a symlink attack on `/tmp/browser.html`.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2013-2105
- https://exchange.xforce.ibmcloud.com/vulnerabilities/84378
- https://github.com/jonleung/show_in_browser
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/show_in_browser/CVE-2013-2105.yml
- http://vapid.dhs.org/advisories/show_in_browser.html
- http://www.openwall.com/lists/oss-security/2013/05/18/4
