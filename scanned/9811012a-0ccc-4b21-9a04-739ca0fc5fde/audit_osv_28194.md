# [M] Saleor Storefront session leak in cache

## Summary
Severity: Medium
Advisory: CVE-2024-29036
Aliases: GHSA-52cq-c7x7-cqw4
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:L/I:N/A:N)
Published: 2024-03-20
Source: https://osv.dev/vulnerability/CVE-2024-29036
Type: osv

## Details
Saleor Storefront is software for building e-commerce experiences. Prior to commit 579241e75a5eb332ccf26e0bcdd54befa33f4783, when any user authenticates in the storefront, anonymous users are able to access their data. The session is leaked through cache and can be accessed by anyone. Users should upgrade to a version that incorporates commit 579241e75a5eb332ccf26e0bcdd54befa33f4783 or later to receive a patch. A possible workaround is to temporarily disable authentication by changing the usage of `createSaleorAuthClient()`.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/29xxx/CVE-2024-29036.json
- https://github.com/saleor/storefront/security/advisories/GHSA-52cq-c7x7-cqw4
- https://nvd.nist.gov/vuln/detail/CVE-2024-29036
- https://github.com/saleor/auth-sdk/commit/56db13407aa35d00b85ec2df042692edd4aea9da
- https://github.com/saleor/saleor-docs/pull/1120
- https://github.com/saleor/storefront/commit/579241e75a5eb332ccf26e0bcdd54befa33f4783
