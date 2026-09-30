# [M] MKTV-1 | Deleveraging Does Not Consider The Flash Fee

## Summary
Severity: Medium
Contest weight: 0.0610
Dataset id: 19571
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The flash fee is not considered when approving the flash lender to pay back the flash loan, therefore the MarketplaceVendor cannot be used to deleverage positions unless the MarketplaceVendor is a flash fee whitelisted address. The MarketplacePurchaser on the other hand does account for the flash fee.

## Recommendation
Consider implementing flash fee support in the MarketplaceVendor. If the MarketplaceVendor contract is intended to always be a flash fee whitelisted address then be careful to always whitelist it.
