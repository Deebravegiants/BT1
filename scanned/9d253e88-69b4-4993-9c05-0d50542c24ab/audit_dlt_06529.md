# [M] VaultManager does not properly enforce `_minMintAmount`

## Summary
Severity: Medium
Chain: Smart contract
Component: Velvet-Capital
Published: 2024-06-20
Source: https://github.com/hats-finance/Velvet-Capital-0x0bb0c08fd9eeaf190064f4c66f11d18182961f77/issues/31
Type: hats-finding

## Details
**Github username:** @deadrosesxyz
**Twitter username:** @deadrosesxyz
**Submission hash (on-chain):** 0x1d56f602663c938c639dbf2b33efd6e3f995ab80fc5aea82d8e39fa8ec246dcf
**Severity:** medium

**Description:**
**Description** 

VaultManager does not properly enforce `_minMintAmount`

**Issue details** 

When depositing user inputs `_minMintAmount` which is the least amount of `PortfolioToken` they're willing to accept. However, if we look at the code of `_depositAndMint`, we'll see that the min mint check is done before fees are charged. 

```solidity
    // Ensure the minted amount meets the user's minimum expectation to mitigate slippage.
    _verifyUserMintedAmount(tokenAmount, _minMintAmount);

    // Mint the calculated portfolio tokens to the user, applying any cooldown periods.
    tokenAmount = _mintTokenAndSetCooldown(_depositFor, tokenAmount);
```

This would allow for a user to receive less tokens than the minimum they've specified, breaking a core invariant 
**Attachments**

1. **Proof of Concept (PoC) File**
<!-- You must provide a file containing a proof of concept (PoC) that demonstrates the vulnerability you have discovered. -->

2. **Revised Code File (Optional)**
<!-- If possible, please provide a second file containing the revised code that offers a potential fix for the vulnerability. This file should include the following information:
- Comment with a clear explanation of the proposed fix.
- The revised code with your suggested changes.
- Any additional comments or explanations that clarify how the fix addresses the vulnerability. -->
