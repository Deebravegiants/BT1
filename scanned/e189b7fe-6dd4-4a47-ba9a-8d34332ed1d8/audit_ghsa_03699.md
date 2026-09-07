# [C] ruby-openid SSRF via claimed_id request

## Summary
Severity: Critical
Advisory: GHSA-fqfj-cmh6-hj49
CVE: CVE-2019-11027
CWE: CWE-918
Ecosystem: RubyGems
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2019-06-13
Source: https://github.com/advisories/GHSA-fqfj-cmh6-hj49
Type: github-advisory

## Affected
- RubyGems: `ruby-openid` — affected >=0 <2.9.0

## Details
Ruby OpenID (aka ruby-openid) through 2.8.0 is vulnerable to SSRF. Ruby-openid performs discovery first, and then verification. This allows an attacker to change the URL used for discovery and trick the server into connecting to the URL, which might be a private server not publicly accessible. Severity can range from medium to critical, depending on how a web application developer chose to employ the ruby-openid library. Developers who based their OpenID integration heavily on the "example app" provided by the project are at highest risk.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-11027
- https://github.com/openid/ruby-openid/issues/122
- https://github.com/openid/ruby-openid/commit/d181a8a2099c64365a1d24b29f6b6b646673a131
- https://github.com/openid/ruby-openid
- https://github.com/openid/ruby-openid/releases/tag/v2.9.0
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/ruby-openid/CVE-2019-11027.yml
- https://lists.debian.org/debian-lts-announce/2019/10/msg00014.html
- https://marc.info/?l=openid-security&m=155154717027534&w=2
- https://security.gentoo.org/glsa/202003-09
