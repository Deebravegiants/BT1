# [M] Wicked gem contains Path traversal vulnerability

## Summary
Severity: Medium
Advisory: GHSA-rprj-g6xc-p5gq
CVE: CVE-2013-4413
CWE: CWE-22
Ecosystem: RubyGems
Published: 2017-10-24
Source: https://github.com/advisories/GHSA-rprj-g6xc-p5gq
Type: github-advisory

## Affected
- RubyGems: `wicked` — affected >=0 <1.0.1

## Details
The Wicked gem prior to v1.0.1 allows a remote attacker to traverse directories on the system via a vulnerability in `controller/concerns/render_redirect.rb`. An attacker can send a specially-crafted URL request containing `%2E%2E%2F` directory traversal sequences to read arbitrary files on the system.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2013-4413
- https://github.com/schneems/wicked/commit/fe31bb2533fffc9d098c69ebeb7afc3b80509f53
- https://exchange.xforce.ibmcloud.com/vulnerabilities/87783
- https://github.com/advisories/GHSA-rprj-g6xc-p5gq
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/wicked/CVE-2013-4413.yml
- https://github.com/schneems/wicked
- https://web.archive.org/web/20210508170740/http://www.securityfocus.com/bid/62891
- http://seclists.org/oss-sec/2013/q4/43
