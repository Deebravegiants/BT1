# [M] Saleor has an Insecure Direct Object Reference (IDOR) in GraphQL API

## Summary
Severity: Medium
Advisory: CVE-2026-24136
Aliases: GHSA-r6fj-f4r9-36gr
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N)
Published: 2026-01-23
Source: https://osv.dev/vulnerability/CVE-2026-24136
Type: osv

## Details
Saleor is an e-commerce platform. Versions 3.2.0 through 3.20.109, 3.21.0-a.0 through 3.21.44 and 3.22.0-a.0 through 3.22.28 have a n Insecure Direct Object Reference (IDOR) vulnerability that allows unauthenticated actors to extract sensitive information in plain text. Orders created before Saleor 3.2.0 could have PIIs exfiltrated. The issue has been patched in Saleor versions: 3.22.29, 3.21.45, and 3.20.110. To workaround, temporarily block non-staff users from fetching order information (the order() GraphQL query) using a WAF.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/24xxx/CVE-2026-24136.json
- https://github.com/saleor/saleor/security/advisories/GHSA-r6fj-f4r9-36gr
- https://nvd.nist.gov/vuln/detail/CVE-2026-24136
- https://github.com/saleor/saleor/commit/5dab1857fbb2801f74e2bfe86f307e4590d9d2fa
- https://github.com/saleor/saleor/commit/718ce1b4fc3aef68eeac1aea0cf1d70a614ba6af
- https://github.com/saleor/saleor/commit/9bcd4f9000b189297eeb3ac88cc28c6c30229153
- https://github.com/saleor/saleor/commit/aeaced8acb5e01055eddec584263f77e517d5944
