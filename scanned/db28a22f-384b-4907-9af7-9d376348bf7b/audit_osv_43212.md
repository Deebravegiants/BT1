# [C] EverShop Missing Authorization on PATCH /api/customers/:id Allows Unauthenticated Account Takeover

## Summary
Severity: Critical
Advisory: CVE-2026-72843
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-08-20
Source: https://osv.dev/vulnerability/CVE-2026-72843
Type: osv

## Details
The customer update route in EverShop is declared with "access": "public" in packages/evershop/src/modules/customer/api/updateCustomer/route.json, which causes the admin authentication middleware to call next() without checking the caller, and no customer-session middleware guards the route; the only middleware in the chain parses the JSON body. The handler in updateCustomer.js then loads the customer by the uuid taken from the URL path and writes the supplied fields back to that record, hashing a password if one is provided, without verifying that the caller owns the record. An unauthenticated request carrying a known customer uuid can therefore overwrite that customer's email address and password and read back the updated record from the 200 response, taking over the account and locking out its owner. Customer uuids are exposed through order confirmation email links and administrative URLs. Version 2.2.1 changes the route to "access": "private".

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/72xxx/CVE-2026-72843.json
- https://github.com/evershopcommerce/evershop/releases/tag/v2.2.1
- https://nvd.nist.gov/vuln/detail/CVE-2026-72843
- https://www.vulncheck.com/advisories/evershop-missing-authorization-on-patch-api-customers-id-allows-unauthenticated-account-takeover
- https://github.com/evershopcommerce/evershop/issues/952
- https://github.com/evershopcommerce/evershop
- https://github.com/evershopcommerce/evershop/blob/v2.1.2/packages/evershop/src/modules/customer/api/updateCustomer/route.json
- https://github.com/evershopcommerce/evershop/blob/v2.1.2/packages/evershop/src/modules/customer/api/updateCustomer/updateCustomer.js
