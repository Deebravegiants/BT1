# [H] Nokogiri has vulnerable dependencies on libxml2 and libxslt

## Summary
Severity: High
Advisory: GHSA-59gp-qqm7-cw4j
CVE: CVE-2021-30560
CWE: CWE-416
Ecosystem: RubyGems
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-59gp-qqm7-cw4j
Type: github-advisory

## Affected
- RubyGems: `nokogiri` — affected >=0 <1.13.2

## Details
Use after free in Blink XSLT in Google Chrome prior to 91.0.4472.164 allowed a remote attacker to potentially exploit heap corruption via a crafted HTML page.

## References
- https://github.com/sparklemotion/nokogiri/security/advisories/GHSA-fq42-c5rg-92c2
- https://nvd.nist.gov/vuln/detail/CVE-2021-30560
- https://chromereleases.googleblog.com/2021/07/stable-channel-update-for-desktop.html
- https://crbug.com/1219209
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/nokogiri/CVE-2021-30560.yml
- https://github.com/sparklemotion/nokogiri
- https://github.com/sparklemotion/nokogiri/releases/tag/v1.13.2
- https://lists.debian.org/debian-lts-announce/2022/09/msg00010.html
- https://security.gentoo.org/glsa/202310-23
- https://www.debian.org/security/2022/dsa-5216
