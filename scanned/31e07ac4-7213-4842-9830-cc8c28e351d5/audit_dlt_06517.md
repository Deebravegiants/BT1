# [M] Don't Allow portfoliotoken share transfers and portfolio token removals during pause state

## Summary
Severity: Medium
Chain: Smart contract
Component: Velvet-Capital
Published: 2024-07-04
Source: https://github.com/hats-finance/Velvet-Capital-0x0bb0c08fd9eeaf190064f4c66f11d18182961f77/issues/102
Type: hats-finding

## Details
**Github username:** @burhankhaja
**Twitter username:** imaybeghost
**Submission hash (on-chain):** 0xa56efc689f4e99d556a9e6b1aa93b0e4897afad1796ef110dcc03c202373e54e
**Severity:** medium

**Description:**
**Description**\
During the pause state, the protocol prevents user deposits and withdrawls (minting and burning) but it doesn't restrict token transfers via `transfer()`. (PortfolioToken.sol)

Similarly, for the asset manager in **Rebalancing** contract, the protocol restricts `updateWeights()` && `updateTokens()` but doesn't restrict token removal functions. Which kinda break the purpose of pausing mechanisms. 

Since Pausing a smart contract is typically done to minimize the impact of exploits on user funds, mitigate security issues, and allow for flexible debugging.

**Attack Scenario**\
*Since this is business logic flaw:*
- Portfoliotoken shares can be easily transfered while the protocol is paused via ERC20 `transfer()` function.
- AssetManager can still Remove portfolio and non-portfolio tokens even during the protocol is paused, which may affect business operations of the protocol

**Recommendation**\
.
- Check if protocol is paused in [_beforeTokenTransfer()](https://github.com/hats-finance/Velvet-Capital-0x0bb0c08fd9eeaf190064f4c66f11d18182961f77/blob/849629b1aacf32d84634d8c4ef1378527bce3bb3/contracts/core/token/PortfolioToken.sol#L114-L131)
```diff
function _beforeTokenTransfer(
    address from,
    address to,
    uint256 amount
  ) internal override {
    super._beforeTokenTransfer(from, to, amount);
    if (from == address(0) || to == address(0)) {
      return;
    }
    if (
      !(assetManagementConfig().transferableToPublic() ||
        (assetManagementConfig().transferable() &&
          assetManagementConfig().whitelistedUsers(to)))
    ) {
      revert ErrorLibrary.Transferprohibited();
    }
```

_Trimmed to 38 lines — full report: https://github.com/hats-finance/Velvet-Capital-0x0bb0c08fd9eeaf190064f4c66f11d18182961f77/issues/102_
