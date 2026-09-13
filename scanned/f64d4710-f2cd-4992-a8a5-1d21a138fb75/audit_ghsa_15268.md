# [M] REXML DoS vulnerability

## Summary
Severity: Medium
Advisory: GHSA-5866-49gr-22v4
CVE: CVE-2024-41946
CWE: CWE-400, CWE-770
Ecosystem: RubyGems
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2024-08-02
Source: https://github.com/advisories/GHSA-5866-49gr-22v4
Type: github-advisory

## Affected
- RubyGems: `rexml` — affected >=0 <3.3.3

## Details
### Impact

The REXML gem before 3.3.2 has a DoS vulnerability when it parses an XML that has many entity expansions with SAX2 or pull parser API.

If you need to parse untrusted XMLs with SAX2 or pull parser API, you may be impacted to this vulnerability.

### Patches

The REXML gem 3.3.3 or later include the patch to fix the vulnerability.

### Workarounds

Don't parse untrusted XMLs with SAX2 or pull parser API.

### References

* https://www.ruby-lang.org/en/news/2008/08/23/dos-vulnerability-in-rexml/ : This is a similar vulnerability
* https://www.ruby-lang.org/en/news/2024/08/01/dos-rexml-cve-2024-41946/: An announce on www.ruby-lang.org

## References
- https://github.com/ruby/rexml/security/advisories/GHSA-5866-49gr-22v4
- https://nvd.nist.gov/vuln/detail/CVE-2024-41946
- https://github.com/ruby/rexml/commit/033d1909a8f259d5a7c53681bcaf14f13bcf0368
- https://github.com/ruby/rexml
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/rexml/CVE-2024-41946.yml
- https://lists.debian.org/debian-lts-announce/2025/01/msg00011.html
- https://security.netapp.com/advisory/ntap-20250117-0007
- https://www.ruby-lang.org/en/news/2008/08/23/dos-vulnerability-in-rexml
- https://www.ruby-lang.org/en/news/2024/08/01/dos-rexml-cve-2024-41946
