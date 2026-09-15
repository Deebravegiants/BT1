# [H] REXML denial of service vulnerability

## Summary
Severity: High
Advisory: GHSA-vmwr-mc7x-5vc3
CVE: CVE-2024-43398
CWE: CWE-776
Ecosystem: RubyGems
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2024-08-22
Source: https://github.com/advisories/GHSA-vmwr-mc7x-5vc3
Type: github-advisory

## Affected
- RubyGems: `rexml` — affected >=0 <3.3.6

## Details
### Impact

The REXML gem before 3.3.6 has a DoS vulnerability when it parses an XML that has many deep elements that have same local name attributes.

If you need to parse untrusted XMLs with tree parser API like `REXML::Document.new`, you may be impacted to this vulnerability. If you use other parser APIs such as stream parser API and SAX2 parser API, this vulnerability is not affected.

### Patches

The REXML gem 3.3.6 or later include the patch to fix the vulnerability.

### Workarounds

Don't parse untrusted XMLs with tree parser API.

### References

* https://www.ruby-lang.org/en/news/2024/08/22/dos-rexml-cve-2024-43398/ : An announce on www.ruby-lang.org

## References
- https://github.com/ruby/rexml/security/advisories/GHSA-vmwr-mc7x-5vc3
- https://nvd.nist.gov/vuln/detail/CVE-2024-43398
- https://github.com/ruby/rexml/commit/7cb5eaeb221c322b9912f724183294d8ce96bae3
- https://github.com/ruby/rexml
- https://github.com/ruby/rexml/releases/tag/v3.3.6
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/rexml/CVE-2024-43398.yml
- https://lists.debian.org/debian-lts-announce/2025/01/msg00011.html
- https://security.netapp.com/advisory/ntap-20250103-0006
- https://www.ruby-lang.org/en/news/2024/08/22/dos-rexml-cve-2024-43398
