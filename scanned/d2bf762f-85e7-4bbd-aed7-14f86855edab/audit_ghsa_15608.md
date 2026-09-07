# [M] Decidim::Admin vulnerable to cross-site scripting (XSS) in the admin activity log

## Summary
Severity: Medium
Advisory: GHSA-rx9f-5ggv-5rh6
CVE: CVE-2024-32034
CWE: CWE-79
Ecosystem: RubyGems
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:H/I:N/A:N (CVSS_V3)
Published: 2024-09-16
Source: https://github.com/advisories/GHSA-rx9f-5ggv-5rh6
Type: github-advisory

## Affected
- RubyGems: `decidim-admin` — affected >=0 <0.27.7
- RubyGems: `decidim-admin` — affected >=0.28.0 <0.28.2

## Details
### Impact
The admin panel is subject to potential XSS attach in case an admin assigns a valuator to a proposal, or does any other action that generates an admin activity log where one of the resources has an XSS crafted. 

### Patches

N/A

### Workarounds

Redirect the pages /admin and /admin/logs to other admin pages to prevent this access (i.e. `/admin/organization/edit`)

### References

OWASP ASVS v4.0.3-5.1.3

## References
- https://github.com/decidim/decidim/security/advisories/GHSA-rx9f-5ggv-5rh6
- https://nvd.nist.gov/vuln/detail/CVE-2024-32034
- https://github.com/decidim/decidim/commit/23fc8d702a4976727f78617f5e42353d67931645
- https://github.com/decidim/decidim/commit/9d79f09a2d38c87feb28725670d6cc1f55c22072
- https://github.com/decidim/decidim/commit/e494235d559be13dd1f8694345e6f6bba762d1c0
- https://github.com/decidim/decidim/commit/ff755e23814aeb56e9089fc08006a5d3faee47b6
- https://github.com/decidim/decidim
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/decidim-admin/CVE-2024-32034.yml
