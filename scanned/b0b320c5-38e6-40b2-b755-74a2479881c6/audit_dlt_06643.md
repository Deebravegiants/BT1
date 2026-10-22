# [H] Users using `withdraw,` will receive more funds than the ones using `redeem`

## Summary
Severity: High
Chain: Smart contract
Component: Euro-Dollar
Published: 2024-11-04
Source: https://github.com/hats-finance/Euro-Dollar-0xa4ccd3b6daa763f729ad59eae75f9cbff7baf2cd/issues/41
Type: hats-finding

## Details
**Github username:** --
**Twitter username:** https://x.com/dobrevaleri
**Submission hash (on-chain):** 0x2de8023e2f80e1c69f7c0012a035c1cb134d0ac18ab38ce1d0cf7509ce6fbd00
**Severity:** high

**Description:**
**Description**\
In the `InvestToken` contract there are two different functions for withdrawing - `withdraw` and `redeem`. The first one is used the withdraw the provided amount of USDE tokens, and the second one is used to withdraw the USDE tokens that are equal to the shares provided.

Also, there are two functions for depositing - `deposit` and `mint`.

The two functions are using `assetsToShares` and `sharesToAssets` from `YieldOracle` to calculate the amounts of shares to be burned and the amount of assets to be minted. However these two functions are using two different prices. This approach is good, because users to solve an issue with the accuring rewards as stated in the docs: " in order ensure that users who flip from invest token to stablecoin do not accrue today's yield, but gets yesterday's conversion rate." ([ref](https://github.com/eurodollar-fi/eurodollar-protocol#yieldoracle)). On the other hand, this approach will result in problems when used in the functions above.

**Attack Scenario**\
1. Two users deposit on the same price at the beggining (for simplicity)
2. The price is increased over the time
3. One of the users withdraws with `withdraw`
4. The other user withdraws with `redeem`

**Attachments**

1. **Proof of Concept (PoC) File**
<!-- You must provide a file containing a proof of concept (PoC) that demonstrates the vulnerability you have discovered. -->

2. **Revised Code File (Optional)**
<!-- If possible, please provide a second file containing the revised code that offers a potential fix for the vulnerability. This file should include the following information:
- Comment with a clear explanation of the proposed fix.
- The revised code with your suggested changes.
- Any additional comments or explanations that clarify how the fix addresses the vulnerability. -->
  
**Files:**
  - PoC.sol (https://hats-backend-prod.herokuapp.com/v1/files/QmbU2ABvTauJLrY3xgMG9zcie8X9a8g9C7VKEjXrxmByHV)
