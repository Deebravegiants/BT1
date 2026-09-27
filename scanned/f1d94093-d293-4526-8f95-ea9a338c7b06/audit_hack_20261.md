# [M] 5.2.1 Cross SeaDrop reentrancy

## Summary
Severity: Medium
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
**Severity:** Medium Risk
**Context:** SeaDrop.sol#L
**Description:** The contract that implementsIERC721SeaDropcan work with multiple Seadrop implementations, for
example, a Seadrop that accepts ETH as payment as well as another Seadrop contract that accepts USDC as
payment at the same time. This introduces the risk of cross contract re-entrancy that can be used to circumvent
themaxMintsPerWalletcheck.
Here's an example of the attack:

1. Consider an ERC721 token that that has two allowedSeaDrop, one that accepts ETH as payment and the
    other that accepts USDC as payment, both with public mints andrestrictedFeeRecipientsset tofalse.
2. LetmaxMintPerWalletbe 1 for both these cases.
3. A malicious fee receiver can now do the following:
    - CallmintPublicfor the Seadrop with ETH fees, which does the_checkMintQuantitycheck and trans-
       fers the fees in ETH to the receiver.
    - The receiver now callsmintPublicfor Seadrop with USDC fees, which does the_checkMintQuantity
       check that still passes.
    - The mint succeeds in the Seadrop-USDC case.
    - The mint succeeds in the Seadrop-ETH case.
    - The minter has 2 NFTs even though it's capped at 1.
Even if a re-entrancy lock is added in the SeaDrop, the same issue persists as it only enters each Seadrop contract
once.
**Recommendation:** Consider adding a reentrancy lock in the ERC-721 contract. Also see the related issue
Reentrancy of fee payment can be used to circumvent max mints per wallet checkabout reentrancy.
