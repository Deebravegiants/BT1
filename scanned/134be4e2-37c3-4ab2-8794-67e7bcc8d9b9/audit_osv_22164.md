# [H] Shopizer - Insufficient Session Expiration

## Summary
Severity: High
Advisory: CVE-2022-23063
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2022-05-03
Source: https://osv.dev/vulnerability/CVE-2022-23063
Type: osv

## Details
In Shopizer versions 2.3.0 to 3.0.1 are vulnerable to Insufficient Session Expiration. When a password has been changed by the user or by an administrator, a user that was already logged in, will still have access to the application even after the password was changed.

## References
- https://github.com/shopizer-ecommerce/shopizer/blob/3.0.1/sm-shop/src/main/java/com/salesmanager/shop/store/api/v1/customer/AuthenticateCustomerApi.java#L213-L237
- https://www.whitesourcesoftware.com/vulnerability-database/CVE-2022-23063
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/23xxx/CVE-2022-23063.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-23063
