# [M] Improper object type validation in saleor

## Summary
Severity: Medium
Advisory: CVE-2022-39275
Aliases: GHSA-xhq8-8c5v-w8ff
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N)
Published: 2022-10-06
Source: https://osv.dev/vulnerability/CVE-2022-39275
Type: osv

## Details
Saleor is a headless, GraphQL commerce platform. In affected versions some GraphQL mutations were not properly checking the ID type input which allowed to access database objects that the authenticated user may not be allowed to access. This vulnerability can be used to expose the following information: Estimating database row counts from tables with a sequential primary key or Exposing staff user and customer email addresses and full name through the `assignNavigation()` mutation. This issue has been patched in main and backported to multiple releases (3.7.17, 3.6.18, 3.5.23, 3.4.24, 3.3.26, 3.2.14, 3.1.24). Users are advised to upgrade. There are no known workarounds for this issue.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/39xxx/CVE-2022-39275.json
- https://github.com/saleor/saleor/security/advisories/GHSA-xhq8-8c5v-w8ff
- https://nvd.nist.gov/vuln/detail/CVE-2022-39275
- https://github.com/saleor/saleor/commit/96e04c092ddcac17b14f2e31554aa02d9006d0ce
