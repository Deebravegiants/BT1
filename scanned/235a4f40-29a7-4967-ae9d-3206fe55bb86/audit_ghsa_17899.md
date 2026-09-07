# [C] Spree has Remote Command Execution vulnerability in search functionality

## Summary
Severity: Critical
Advisory: GHSA-97vm-c39p-jr86
CVE: CVE-2011-10019
CWE: CWE-1321, CWE-94
Ecosystem: RubyGems
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2025-08-13
Source: https://github.com/advisories/GHSA-97vm-c39p-jr86
Type: github-advisory

## Affected
- RubyGems: `spree` — affected >=0 <0.60.2

## Details
Spreecommerce versions prior to 0.60.2 contains a remote command execution vulnerability in its search functionality. The application fails to properly sanitize input passed via the search[send][] parameter, which is dynamically invoked using Ruby’s send method. This allows attackers to execute arbitrary shell commands on the server without authentication.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2011-10019
- https://github.com/orgs/spree
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/spree/CVE-2011-10019.yml
- https://github.com/spree/spree
- https://raw.githubusercontent.com/rapid7/metasploit-framework/master/modules/exploits/multi/http/spree_search_exec.rb
- https://web.archive.org/web/20111009192436/http://spreecommerce.com/blog/2011/10/05/remote-command-product-group
- https://www.exploit-db.com/exploits/17941
- https://www.vulncheck.com/advisories/spreecommerce-search-parameter-rce
