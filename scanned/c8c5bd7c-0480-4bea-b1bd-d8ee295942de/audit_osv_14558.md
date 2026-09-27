# [M] CVE-2019-1010304

## Summary
Severity: Medium
Advisory: CVE-2019-1010304
CVSS: 5.3 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N)
Published: 2019-07-15
Source: https://osv.dev/vulnerability/CVE-2019-1010304
Type: osv

## Details
Saleor Issue was introduced by merge commit: e1b01bad0703afd08d297ed3f1f472248312cc9c. This commit was released as part of 2.0.0 release is affected by: Incorrect Access Control. The impact is: Important. The component is: ProductVariant type in GraphQL API. The attack vector is: Unauthenticated user can access the GraphQL API (which is by default publicly exposed under `/graphql/` URL) and fetch products data which may include admin-restricted shop's revenue data. The fixed version is: 2.3.1.

## References
- https://github.com/mirumee/saleor/issues/3768
