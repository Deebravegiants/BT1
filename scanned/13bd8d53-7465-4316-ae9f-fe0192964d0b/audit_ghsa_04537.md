# [M] Craft Commerce: Partial Payment Amount Without Lower Bound Validation

## Summary
Severity: Medium
Advisory: GHSA-78vr-q6cf-c7p6
CWE: CWE-1284, CWE-20
Ecosystem: Packagist
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:L/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-06-19
Source: https://github.com/advisories/GHSA-78vr-q6cf-c7p6
Type: github-advisory

## Affected
- Packagist: `craftcms/commerce` — affected >=5.0.0 <5.6.5
- Packagist: `craftcms/commerce` — affected >=4.0.0 <4.11.2

## Details
### Summary

The `Order::setPaymentAmount()` method accepts any float value without enforcing a minimum positive amount. The PaymentsController casts the user-supplied 'paymentAmount' parameter directly to float with no lower-bound check. 

### Details

When the store has 'Allow Partial Payment on Checkout' enabled, a user can submit a payment amount of $0.00 or even a negative value, potentially marking orders as paid without a valid transaction.

<img width="690" height="80" alt="image" src="https://github.com/user-attachments/assets/78b653a6-ccae-4ce4-b71b-fc38a7757d73" />

<img width="761" height="200" alt="image" src="https://github.com/user-attachments/assets/665a235f-62c2-45fe-aa41-c3f266881c77" />

### PoC

_Complete instructions, including specific configuration details, to reproduce the vulnerability._
<img width="606" height="144" alt="image" src="https://github.com/user-attachments/assets/a04a6de2-7c5f-4837-aed6-58756e246b80" />


### Impact
On stores with partial payment enabled, a customer may be able to set an arbitrarily small payment amount. Gateway behavior varies — some will process $0.00 transactions, effectively giving free order fulfillment.

**Remediation**

<img width="718" height="98" alt="image" src="https://github.com/user-attachments/assets/aa64b696-9749-45e4-97f6-8d7299cdf1d6" />

## References
- https://github.com/craftcms/commerce/security/advisories/GHSA-78vr-q6cf-c7p6
- https://github.com/craftcms/commerce/commit/9a88392b3074aa132a9455d4f4b582411df52c74
- https://github.com/craftcms/commerce
