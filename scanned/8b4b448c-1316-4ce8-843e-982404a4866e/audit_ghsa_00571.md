# [M] Rack vulnerable to Cross-site Scripting

## Summary
Severity: Medium
Advisory: GHSA-5r2p-j47h-mhpg
CVE: CVE-2018-16471
CWE: CWE-79
Ecosystem: RubyGems
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2018-11-15
Source: https://github.com/advisories/GHSA-5r2p-j47h-mhpg
Type: github-advisory

## Affected
- RubyGems: `rack` — affected >=2.0.0 <2.0.6
- RubyGems: `rack` — affected >=0 <1.6.11

## Details
There is a possible XSS vulnerability in Rack before 2.0.6 and 1.6.11. Carefully crafted requests can impact the data returned by the `scheme` method on `Rack::Request`. Applications that expect the scheme to be limited to 'http' or 'https' and do not escape the return value could be vulnerable to an XSS attack. Note that applications using the normal escaping mechanisms provided by Rails may not impacted, but applications that bypass the escaping mechanisms, or do not use them may be vulnerable.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-16471
- https://github.com/rack/rack
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/rack/CVE-2018-16471.yml
- https://groups.google.com/forum/#!topic/ruby-security-ann/NAalCee8n6o
- https://groups.google.com/forum/#!topic/rubyonrails-security/GKsAFT924Ag
- https://lists.debian.org/debian-lts-announce/2018/11/msg00022.html
- https://usn.ubuntu.com/4089-1
- http://lists.opensuse.org/opensuse-security-announce/2019-06/msg00032.html
- http://lists.opensuse.org/opensuse-security-announce/2020-02/msg00016.html
