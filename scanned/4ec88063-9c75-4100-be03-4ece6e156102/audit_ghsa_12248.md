# [M] Rack Vulnerable to Path Traversal

## Summary
Severity: Medium
Advisory: GHSA-85r7-w5mv-c849
CVE: CVE-2013-0262
CWE: CWE-22
Ecosystem: RubyGems
Published: 2017-10-24
Source: https://github.com/advisories/GHSA-85r7-w5mv-c849
Type: github-advisory

## Affected
- RubyGems: `rack` — affected >=1.5.0 <1.5.2
- RubyGems: `rack` — affected >=1.4.0 <1.4.5

## Details
`rack/file.rb` (`Rack::File`) in Rack 1.5.x before 1.5.2 and 1.4.x before 1.4.5 allows attackers to access arbitrary files outside the intended root directory via a crafted `PATH_INFO` environment variable, probably a directory traversal vulnerability that is remotely exploitable, aka "symlink path traversals."

## References
- https://nvd.nist.gov/vuln/detail/CVE-2013-0262
- https://github.com/rack/rack/commit/6f237e4c9fab649d3750482514f0fde76c56ab30
- https://bugzilla.redhat.com/show_bug.cgi?id=909071
- https://bugzilla.redhat.com/show_bug.cgi?id=909072
- https://gist.github.com/rentzsch/4736940
- https://github.com/rack/rack
- https://github.com/rack/rack/blob/master/lib/rack/file.rb#L56
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/rack/CVE-2013-0262.yml
- https://groups.google.com/forum/#!msg/rack-devel/bf937jPZxJM/1s6x95vIhmAJ
- https://groups.google.com/forum/#!msg/rack-devel/mZsuRonD7G8/DpZIOmMLbOgJ
- http://lists.opensuse.org/opensuse-updates/2013-03/msg00048.html
