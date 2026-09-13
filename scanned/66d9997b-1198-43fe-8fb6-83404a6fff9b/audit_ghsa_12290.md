# [M] sprockets vulnerable to Path Traversal

## Summary
Severity: Medium
Advisory: GHSA-33pp-3763-mrfp
CVE: CVE-2014-7819
CWE: CWE-22
Ecosystem: RubyGems
Published: 2017-10-24
Source: https://github.com/advisories/GHSA-33pp-3763-mrfp
Type: github-advisory

## Affected
- RubyGems: `sprockets` — affected >=0 <2.0.5
- RubyGems: `sprockets` — affected >=2.1.0 <2.1.4
- RubyGems: `sprockets` — affected >=2.2.0 <2.2.3
- RubyGems: `sprockets` — affected >=2.3.0 <2.3.3
- RubyGems: `sprockets` — affected >=2.4.0 <2.4.6
- RubyGems: `sprockets` — affected >=2.5.0 <2.5.1
- RubyGems: `sprockets` — affected >=2.6.0 <2.7.1
- RubyGems: `sprockets` — affected >=2.8.0 <2.8.3
- RubyGems: `sprockets` — affected >=2.9.0 <2.9.4
- RubyGems: `sprockets` — affected >=2.10.0 <2.10.2
- RubyGems: `sprockets` — affected >=2.11.0 <2.11.3
- RubyGems: `sprockets` — affected >=2.12.0 <2.12.3

## Details
Multiple directory traversal vulnerabilities in `server.rb` in Sprockets before 2.0.5, 2.1.x before 2.1.4, 2.2.x before 2.2.3, 2.3.x before 2.3.3, 2.4.x before 2.4.6, 2.5.x before 2.5.1, 2.6.x and 2.7.x before 2.7.1, 2.8.x before 2.8.3, 2.9.x before 2.9.4, 2.10.x before 2.10.2, 2.11.x before 2.11.3, 2.12.x before 2.12.3, and 3.x before 3.0.0.beta.3, as distributed with Ruby on Rails 3.x and 4.x, allow remote attackers to determine the existence of files outside the application root via a ../ (dot dot slash) sequence with (1) double slashes or (2) URL encoding.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2014-7819
- https://access.redhat.com/errata/RHBA-2015:1100
- https://access.redhat.com/security/cve/CVE-2014-7819
- https://bugzilla.redhat.com/show_bug.cgi?id=1161527
- https://groups.google.com/forum/#!topic/rubyonrails-security/doAVp0YaTqY
- https://groups.google.com/forum/message/raw?msg=rubyonrails-security/doAVp0YaTqY/aHFngBqNBoAJ
- https://groups.google.com/forum/message/raw?msg=rubyonrails-security/wQBeGXqGs3E/JqUMB6fhh3gJ
- http://lists.opensuse.org/opensuse-updates/2014-11/msg00103.html
- http://lists.opensuse.org/opensuse-updates/2014-11/msg00105.html
- http://lists.opensuse.org/opensuse-updates/2014-11/msg00110.html
- http://lists.opensuse.org/opensuse-updates/2014-11/msg00111.html
