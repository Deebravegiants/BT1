# [M] Rack arbitrary code execution via timing attack

## Summary
Severity: Medium
Advisory: GHSA-xc85-32mf-xpv8
CVE: CVE-2013-0263
Ecosystem: RubyGems
Published: 2022-05-05
Source: https://github.com/advisories/GHSA-xc85-32mf-xpv8
Type: github-advisory

## Affected
- RubyGems: `rack` — affected >=1.5.0 <1.5.2
- RubyGems: `rack` — affected >=1.4.0 <1.4.5
- RubyGems: `rack` — affected >=1.3.0 <1.3.10
- RubyGems: `rack` — affected >=1.2.0 <1.2.8
- RubyGems: `rack` — affected >=1.1.0 <1.1.6

## Details
Rack::Session::Cookie in Rack 1.5.x before 1.5.2, 1.4.x before 1.4.5, 1.3.x before 1.3.10, 1.2.x before 1.2.8, and 1.1.x before 1.1.6 allows remote attackers to guess the session cookie, gain privileges, and execute arbitrary code via a timing attack involving an HMAC comparison function that does not run in constant time.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2013-0263
- https://github.com/rack/rack/commit/0cd7e9aa397f8ebb3b8481d67dbac8b4863a7f07
- https://github.com/rack/rack/commit/9a81b961457805f6d1a5c275d053068440421e11
- https://bugzilla.redhat.com/show_bug.cgi?id=909071
- https://gist.github.com/codahale/f9f3781f7b54985bee94
- https://github.com/rack/rack
- https://groups.google.com/d/msg/rack-devel/xKrHVWeNvDM/4ZGA576CnK4J
- https://groups.google.com/forum/#!msg/rack-devel/RnQxm6i13C4/xfakH81yWvgJ
- https://groups.google.com/forum/#!msg/rack-devel/bf937jPZxJM/1s6x95vIhmAJ
- https://groups.google.com/forum/#!msg/rack-devel/hz-liLb9fKE/8jvVWU6xYiYJ
- https://groups.google.com/forum/#!msg/rack-devel/mZsuRonD7G8/DpZIOmMLbOgJ
- http://lists.opensuse.org/opensuse-updates/2013-03/msg00048.html
- http://rhn.redhat.com/errata/RHSA-2013-0686.html
- http://www.debian.org/security/2013/dsa-2783
