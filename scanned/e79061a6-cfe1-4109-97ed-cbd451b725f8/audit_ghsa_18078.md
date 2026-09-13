# [C] Spree Commerce is vulnerable to RCE through Search API

## Summary
Severity: Critical
Advisory: GHSA-x485-rhg3-cqr4
CVE: CVE-2011-10026
CWE: CWE-78, CWE-94
Ecosystem: RubyGems
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2025-08-20
Source: https://github.com/advisories/GHSA-x485-rhg3-cqr4
Type: github-advisory

## Affected
- RubyGems: `spree` — affected >=0.30.0.beta1 <0.50.0
- RubyGems: `rd_searchlogic` — affected >=0

## Details
Spreecommerce versions prior to 0.50.x contain a remote command execution vulnerability in the API's search functionality. Improper input sanitation allows attackers to inject arbitrary shell commands via the search[instance_eval] parameter, which is dynamically invoked using Ruby’s send method. This flaw enables unauthenticated attackers to execute commands on the server.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2011-10026
- https://github.com/spree/spree/commit/0a9a360c590829d8a377ceae0cf997bbbbcc2df4
- https://github.com/spree/spree/commit/3b559e7219f3681184be409ad00cd34a34a37978
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/rd_searchlogic/CVE-2011-10026.yml
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/spree/CVE-2011-10026.yml
- https://github.com/spree
- https://github.com/spree/spree
- https://raw.githubusercontent.com/rapid7/metasploit-framework/master/modules/exploits/multi/http/spree_searchlogic_exec.rb
- https://web.archive.org/web/20111120023342/http://spreecommerce.com/blog/2011/04/19/security-fixes
- https://www.exploit-db.com/exploits/17199
- https://www.vulncheck.com/advisories/spreecommerce-api-rce
