# [H] Decidim has a cross-site scripting vulnerability in the version control page

## Summary
Severity: High
Advisory: GHSA-cc4g-m3g7-xmw8
CVE: CVE-2024-41673
CWE: CWE-79
Ecosystem: RubyGems
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:L/A:N (CVSS_V3)
Published: 2024-10-01
Source: https://github.com/advisories/GHSA-cc4g-m3g7-xmw8
Type: github-advisory

## Affected
- RubyGems: `decidim` — affected >=0 <0.27.8

## Details
### Impact

The version control feature used in resources is subject to potential cross-site scripting (XSS) attack through a malformed URL. 

### Workarounds

Not available

### References

OWASP ASVS v4.0.3-5.1.3

### Credits

This issue was discovered in a security audit organized by [Open Source Politics](https://opensourcepolitics.eu/) against Decidim done during July 2025.

## References
- https://github.com/decidim/decidim/security/advisories/GHSA-cc4g-m3g7-xmw8
- https://nvd.nist.gov/vuln/detail/CVE-2024-41673
- https://github.com/decidim/decidim/commit/8a18c8b1ee85a1b35ee0d8d5893f218695d15637
- https://github.com/decidim/decidim
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/decidim/CVE-2024-41673.yml
