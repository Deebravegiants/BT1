# [M] REXML ReDoS vulnerability

## Summary
Severity: Medium
Advisory: GHSA-2rxp-v6pw-ch6m
CVE: CVE-2024-49761
CWE: CWE-1333
Ecosystem: RubyGems
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2024-10-28
Source: https://github.com/advisories/GHSA-2rxp-v6pw-ch6m
Type: github-advisory

## Affected
- RubyGems: `rexml` — affected >=0 <3.3.9

## Details
### Impact

The REXML gem before 3.3.9 has a ReDoS vulnerability when it parses an XML that has many digits between `&#` and `x...;` in a hex numeric character reference (`&#x...;`).

This does not happen with Ruby 3.2 or later. Ruby 3.1 is the only affected maintained Ruby. Note that Ruby 3.1 will reach EOL on 2025-03.

### Patches

The REXML gem 3.3.9 or later include the patch to fix the vulnerability.

### Workarounds

Use Ruby 3.2 or later instead of Ruby 3.1.

### References

* https://www.ruby-lang.org/en/news/2024/10/28/redos-rexml-cve-2024-49761/: An announce on www.ruby-lang.org

## References
- https://github.com/ruby/rexml/security/advisories/GHSA-2rxp-v6pw-ch6m
- https://nvd.nist.gov/vuln/detail/CVE-2024-49761
- https://github.com/ruby/rexml/commit/ce59f2eb1aeb371fe1643414f06618dbe031979f
- https://github.com/ruby/rexml
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/rexml/CVE-2024-49761.yml
- https://lists.debian.org/debian-lts-announce/2025/01/msg00011.html
- https://security.netapp.com/advisory/ntap-20241227-0004
- https://www.ruby-lang.org/en/news/2024/10/28/redos-rexml-cve-2024-49761
