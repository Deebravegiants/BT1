# [H] Nokogiri gem, via libxml, is affected by DoS vulnerabilities

## Summary
Severity: High
Advisory: GHSA-r58r-74gx-6wx3
CVE: CVE-2017-15412
CWE: CWE-416
Ecosystem: RubyGems
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-r58r-74gx-6wx3
Type: github-advisory

## Affected
- RubyGems: `nokogiri` — affected >=0 <1.8.2

## Details
Use after free in libxml2 before 2.9.5, as used in Google Chrome prior to 63.0.3239.84 and other products, allowed a remote attacker to potentially exploit heap corruption via a crafted HTML page.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-15412
- https://github.com/sparklemotion/nokogiri/issues/1714
- https://access.redhat.com/errata/RHSA-2017:3401
- https://access.redhat.com/errata/RHSA-2018:0287
- https://bugzilla.gnome.org/show_bug.cgi?id=783160
- https://chromereleases.googleblog.com/2017/12/stable-channel-update-for-desktop.html
- https://crbug.com/727039
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/nokogiri/CVE-2017-15412.yml
- https://lists.debian.org/debian-lts-announce/2017/12/msg00014.html
- https://security.gentoo.org/glsa/201801-03
- https://web.archive.org/web/20201208155618/http://www.securitytracker.com/id/1040348
- https://www.debian.org/security/2018/dsa-4086
