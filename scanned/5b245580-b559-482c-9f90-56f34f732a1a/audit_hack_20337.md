# [M] 5.2.5 Using a singletokenRecipientinVeryFastRoutercould result in locked NFTs

## Summary
Severity: Medium
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
**Severity:** Medium Risk

**Context:** VeryFastRouter.sol#L45, VeryFastRouter.sol#L134-L139, VeryFastRouter.sol#L158-L210,
LSSVMRouter.sol#L42-L

**Description:** VeryFastRouteruses a singletokenRecipientaddress for both ETH/tokens and NFTs, unlike
LSSVMRouterwhich uses a separatetokenRecipientandnftRecipient.

It is error-prone to have a singletokenRecipientreceive both tokens and NFTs, especially when the other/existing
LSSVMRouterhas a separatenftRecipient.VeryFastRouter.swap()sends both sell order tokens totokenRe-
cipientand buy order NFTs totokenRecipient. Front-ends integrating with both routers (or migrating to the new
one) may surprise users by sending both tokens+NFTs to the same address when interacting with this router. This
coupled with the use ofnft.transferFrom()may result in NFTs being sent to contracts that are not ERC-
receivers and get them locked forever.

**Recommendation:** Consider a separatenftRecipientin orders similar toLSSVMRouter.

**Sudorandom Labs:** Solved in PR#57.

**Spearbit:** Verified that this is fixed by PR#57.
