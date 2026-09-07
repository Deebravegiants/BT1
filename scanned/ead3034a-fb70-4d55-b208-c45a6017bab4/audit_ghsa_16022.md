# [M] decidim-meetings Cross-site scripting vulnerability in the online or hybrid meeting embeds

## Summary
Severity: Medium
Advisory: GHSA-j4h6-gcj7-7v9v
CVE: CVE-2024-45594
CWE: CWE-79
Ecosystem: RubyGems
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:R/S:C/C:H/I:H/A:N (CVSS_V3)
Published: 2024-11-13
Source: https://github.com/advisories/GHSA-j4h6-gcj7-7v9v
Type: github-advisory

## Affected
- RubyGems: `decidim-meetings` — affected >=0.28.0 <0.28.3

## Details
### Impact

The meeting embeds feature used in the online or hybrid meetings is subject to potential XSS attack through a malformed URL.

### Patches

Not available

### Workarounds

Disable the creation of meetings by participants in the meeting component.

### References

OWASP ASVS v4.0.3-5.1.3

### Credits

This issue was discovered in a security audit organized by mitgestalten Partizipationsbüro against Decidim. The security audit was implemented by the Austrian Institute of Technology.

## References
- https://github.com/decidim/decidim/security/advisories/GHSA-j4h6-gcj7-7v9v
- https://nvd.nist.gov/vuln/detail/CVE-2024-45594
- https://github.com/decidim/decidim
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/decidim-meetings/CVE-2024-45594.yml
