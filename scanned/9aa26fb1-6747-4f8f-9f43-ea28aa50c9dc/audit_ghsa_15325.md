# [M] REXML DoS vulnerability

## Summary
Severity: Medium
Advisory: GHSA-r55c-59qm-vjw6
CVE: CVE-2024-41123
CWE: CWE-400, CWE-770
Ecosystem: RubyGems
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2024-08-01
Source: https://github.com/advisories/GHSA-r55c-59qm-vjw6
Type: github-advisory

## Affected
- RubyGems: `rexml` — affected >=0 <3.3.3

## Details
### Impact

The REXML gem before 3.3.2 has some DoS vulnerabilities when it parses an XML that has many specific characters such as whitespace character, `>]` and `]>`.

If you need to parse untrusted XMLs, you may be impacted to these vulnerabilities.

### Patches

The REXML gem 3.3.3 or later include the patches to fix these vulnerabilities.

### Workarounds

Don't parse untrusted XMLs.

### References

* https://github.com/ruby/rexml/security/advisories/GHSA-vg3r-rm7w-2xgh : This is a similar vulnerability
* https://github.com/ruby/rexml/security/advisories/GHSA-4xqq-m2hx-25v8 : This is a similar vulnerability
* https://www.ruby-lang.org/en/news/2024/08/01/dos-rexml-cve-2024-41123/: An announce on www.ruby-lang.org

## References
- https://github.com/ruby/rexml/security/advisories/GHSA-4xqq-m2hx-25v8
- https://github.com/ruby/rexml/security/advisories/GHSA-r55c-59qm-vjw6
- https://github.com/ruby/rexml/security/advisories/GHSA-vg3r-rm7w-2xgh
- https://nvd.nist.gov/vuln/detail/CVE-2024-41123
- https://github.com/ruby/rexml
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/rexml/CVE-2024-41123.yml
- https://lists.debian.org/debian-lts-announce/2025/01/msg00011.html
- https://security.netapp.com/advisory/ntap-20241227-0005
- https://www.ruby-lang.org/en/news/2024/08/01/dos-rexml-cve-2024-41123
