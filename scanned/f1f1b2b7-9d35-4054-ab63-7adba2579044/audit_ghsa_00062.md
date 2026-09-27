# [C] Nokogiri does not forbid namespace nodes in XPointer ranges

## Summary
Severity: Critical
Advisory: GHSA-fr52-4hqw-p27f
CVE: CVE-2016-4658
CWE: CWE-119
Ecosystem: RubyGems
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2018-08-21
Source: https://github.com/advisories/GHSA-fr52-4hqw-p27f
Type: github-advisory

## Affected
- RubyGems: `nokogiri` — affected >=0 <1.7.1

## Details
xpointer.c in libxml2 before 2.9.5 (as used in nokogiri before 1.7.1 amongst other products) does not forbid namespace nodes in XPointer ranges, which allows remote attackers to execute arbitrary code or cause a denial of service (use-after-free and memory corruption) via a crafted XML document.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2016-4658
- https://git.gnome.org/browse/libxml2/commit/?id=c1d1f7121194036608bf555f08d3062a36fd344b
- https://security.gentoo.org/glsa/201701-37
- https://support.apple.com/HT207141
- https://support.apple.com/HT207142
- https://support.apple.com/HT207143
- https://support.apple.com/HT207170
- http://lists.apple.com/archives/security-announce/2016/Sep/msg00006.html
- http://lists.apple.com/archives/security-announce/2016/Sep/msg00008.html
- http://lists.apple.com/archives/security-announce/2016/Sep/msg00010.html
- http://lists.apple.com/archives/security-announce/2016/Sep/msg00011.html
