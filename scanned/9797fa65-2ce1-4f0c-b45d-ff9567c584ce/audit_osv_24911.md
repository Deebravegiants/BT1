# [M] CVE-2023-28362

## Summary
Severity: Medium
Advisory: CVE-2023-28362
Aliases: GHSA-4g8v-vg43-wpgf
CVSS: 4.0 (CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N)
Published: 2025-01-09
Source: https://osv.dev/vulnerability/CVE-2023-28362
Type: osv

## Details
The redirect_to method in Rails allows provided values to contain characters which are not legal in an HTTP header value. This results in the potential for downstream services which enforce RFC compliance on HTTP response headers to remove the assigned Location header.

## References
- https://discuss.rubyonrails.org/t/cve-2023-28362-possible-xss-via-user-supplied-values-to-redirect-to/83132
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/28xxx/CVE-2023-28362.json
- https://github.com/advisories/GHSA-4g8v-vg43-wpgf
- https://nvd.nist.gov/vuln/detail/CVE-2023-28362
- https://security.netapp.com/advisory/ntap-20250502-0009/
- https://github.com/rails/rails/commit/1c3f93d1e90a3475f9ae2377ead25ccf11f71441
- https://github.com/rails/rails/commit/69e37c84e3f77d75566424c7d0015172d6a6fac5
