# [M] Decidim cross-site scripting (XSS) in the pagination

## Summary
Severity: Medium
Advisory: GHSA-7cx8-44pc-xv3q
CVE: CVE-2024-32469
CWE: CWE-79
Ecosystem: RubyGems
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:L/A:N (CVSS_V3)
Published: 2024-07-10
Source: https://github.com/advisories/GHSA-7cx8-44pc-xv3q
Type: github-advisory

## Affected
- RubyGems: `decidim` — affected >=0 <0.27.6
- RubyGems: `decidim` — affected >=0.28.0.rc1 <0.28.1

## Details
### Impact

The pagination feature used in searches and filters is subject to potential XSS attack through a malformed URL using the GET parameter `per_page`. 

### Patches

Not available

### Workarounds

Not available

### References

OWASP ASVS v4.0.3-5.1.3

### Credits

This issue was discovered in a security audit organized by the [mitgestalten Partizipationsbüro](https://partizipationsbuero.at/) and funded by [netidee](https://www.netidee.at/) against Decidim done during April 2024. The security audit was implemented by  [AIT Austrian Institute of Technology GmbH](https://www.ait.ac.at/),

## References
- https://github.com/decidim/decidim/security/advisories/GHSA-7cx8-44pc-xv3q
- https://nvd.nist.gov/vuln/detail/CVE-2024-32469
- https://github.com/decidim/decidim
- https://github.com/decidim/decidim/releases/tag/v0.27.6
- https://github.com/decidim/decidim/releases/tag/v0.28.1
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/decidim/CVE-2024-32469.yml
