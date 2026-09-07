# [H] RedCloth Regular Expression Denial of Service issue

## Summary
Severity: High
Advisory: GHSA-qcm3-vfq5-wfr2
CVE: CVE-2023-31606
CWE: CWE-1333
Ecosystem: RubyGems
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2023-06-06
Source: https://github.com/advisories/GHSA-qcm3-vfq5-wfr2
Type: github-advisory

## Affected
- RubyGems: `RedCloth` — affected >=0 <4.3.3

## Details
A Regular Expression Denial of Service (ReDoS) issue was discovered in the `sanitize_html` function of RedCloth gem. This vulnerability allows attackers to cause a Denial of Service (DoS) via supplying a crafted payload.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-31606
- https://github.com/jgarber/redcloth/issues/73
- https://github.com/jgarber/redcloth/commit/8b1327688fef8e6617792054ef299d7bc74c0a1e
- https://github.com/e23e/CVE-2023-31606#readme
- https://github.com/jgarber/redcloth
- https://github.com/jgarber/redcloth/blob/v4.3.2/lib/redcloth/formatters/html.rb#L327
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/RedCloth/CVE-2023-31606.yml
- https://lists.debian.org/debian-lts-announce/2023/07/msg00002.html
- https://security.gentoo.org/glsa/202401-14
