Based on my analysis, I found a direct analog to the reported vulnerability.

---

### Title
Single `maxNegligibleAmount` Threshold Applied Uniformly Across All LST Assets Ignores Per-Asset ETH Value — (`File: contracts/LRTDepositPool.sol`)

### Summary
`LRTDepositPool._checkResidueLSTBalance` uses a single protocol-wide `maxNegligibleAmount` value to gate NodeDelegator removal for **every** supported LST asset, without converting each asset's balance to its ETH-denominated value. Because different LSTs trade at different ETH exchange rates, the same raw-token threshold represents materially different ETH values across assets. When an NDC is removed with a residual balance that passes this check, those assets are permanently stranded — no longer tracked by the protocol and inaccessible to users.

### Finding Description
`LRTDepositPool` stores a single `maxNegligibleAmount` state variable: [1](#0-0) 

The admin sets it via: [2](#0-1) 

When a NodeDelegator is removed from the queue, `_checkResidueLSTBalance` iterates over every supported LST and compares its raw token balance against this single threshold: [3](#0-2) 

The comparison on line 642 is purely in raw token units. No oracle price is consulted. If `assetBalance <= maxNegligibleAmount`, the check passes for that asset and the NDC is removed — even if the residual balance represents significant ETH value for a higher-priced LST.

The same flaw exists for the ETH residue check: [4](#0-3) 

Once the NDC is removed from `nodeDelegatorQueue` and `isNodeDelegator` is zeroed out, the protocol has no further accounting of assets held by that contract. The stranded assets are excluded from `getTotalAssetDeposits`, which feeds the rsETH price oracle, causing the rsETH/ETH rate to silently decrease — diluting all rsETH holders. [5](#0-4) 

### Impact Explanation
Assets remaining in a dequeued NodeDelegator are permanently frozen: they are not reachable through any user-facing withdrawal path, and they are excluded from TVL accounting, causing a permanent, irreversible reduction in the rsETH exchange rate. This constitutes both **permanent freezing of funds** and **protocol insolvency** (rsETH holders receive fewer assets than they are owed).

### Likelihood Explanation
The admin sets one `maxNegligibleAmount` value intended to cover all assets. Because all current LSTs are ETH-denominated and roughly 1:1 with ETH, the admin may calibrate the threshold against stETH (e.g., `1e17` ≈ 0.1 stETH ≈ $300) without realising the same raw-token threshold applies to every other supported LST. If a new LST is added whose exchange rate differs — or if the threshold is simply set too generously — the residual balance that "passes" the check can represent substantial ETH value. The admin is acting in good faith following the protocol's intended removal flow; no malicious intent is required.

### Recommendation
Replace the single `maxNegligibleAmount` with a per-asset negligible threshold, or convert each asset's balance to its ETH-denominated value (using `LRTOracle.getAssetPrice`) before comparing against the threshold. For example:

```solidity
uint256 assetBalanceInETH = assetBalance * lrtOracle.getAssetPrice(supportedAssets[i]) / 1e18;
if (assetBalanceInETH > maxNegligibleAmount) {
    revert NodeDelegatorHasAssetBalance(supportedAssets[i], assetBalance);
}
```

This mirrors the recommendation in the original report: compute the notional value of the residual before comparing it to the dust threshold, and express the threshold in the common unit (ETH).

### Proof of Concept
1. Admin sets `maxNegligibleAmount = 1e17` (0.1 tokens), calibrated against stETH ≈ 0.1 ETH ≈ $300.
2. A new LST `tokenX` is added to the protocol with an ETH exchange rate of `2e18` (2 ETH per token).
3. An NDC accumulates `1e17` tokenX (= 0.2 ETH ≈ $600) as a residual after most assets are moved out.
4. Admin calls `removeNodeDelegatorContractFromQueue(ndc)`.
5. `_checkResidueLSTBalance` evaluates `1e17 > 1e17` → `false` → no revert.
6. The NDC is removed; `isNodeDelegator[ndc] = 0`; `nodeDelegatorQueue` no longer contains it.
7. The `1e17` tokenX held by the NDC is excluded from all future `getTotalAssetDeposits` calls, permanently reducing the rsETH price and freezing those user funds with no recovery path. [6](#0-5)

### Citations

**File:** contracts/LRTDepositPool.sol (L35-36)
```text
    /// @notice maximum amount that can be ignored
    uint256 public maxNegligibleAmount;
```

**File:** contracts/LRTDepositPool.sol (L274-276)
```text
    function setMaxNegligibleAmount(uint256 maxNegligibleAmount_) external onlyLRTAdmin {
        maxNegligibleAmount = maxNegligibleAmount_;
        emit MaxNegligibleAmountUpdated(maxNegligibleAmount_);
```

**File:** contracts/LRTDepositPool.sol (L385-397)
```text
    function getTotalAssetDeposits(address asset) public view override returns (uint256 totalAssetDeposit) {
        (
            uint256 assetLyingInDepositPool,
            uint256 assetLyingInNDCs,
            uint256 assetStakedInEigenLayer,
            uint256 assetUnstakingFromEigenLayer,
            uint256 assetLyingInConverter,
            uint256 assetLyingUnstakingVault
        ) = getAssetDistributionData(asset);
        uint256 effectiveAssetWithEigenLayer = assetStakedInEigenLayer + assetUnstakingFromEigenLayer;
        return (assetLyingInDepositPool + assetLyingInNDCs + effectiveAssetWithEigenLayer + assetLyingInConverter
                + assetLyingUnstakingVault);
    }
```

**File:** contracts/LRTDepositPool.sol (L579-597)
```text
    function _removeNodeDelegatorContractFromQueue(address nodeDelegatorAddress) internal {
        // 1. check if node delegator contract is in queue and find Index
        uint256 ndcIndex = _getNDCIndex(nodeDelegatorAddress);

        // 2. revert if node delegator contract has any asset balances.
        // 2.1 check if NDC has native ETH balance in eigen layer or/and in itself.
        _checkResidueEthBalance(nodeDelegatorAddress);
        // 2.2  check if NDC has LST balance
        _checkResidueLSTBalance(nodeDelegatorAddress);

        // 3. remove node delegator contract from queue
        // 3.1 remove from isNodeDelegator mapping
        isNodeDelegator[nodeDelegatorAddress] = 0;
        // 3.2 remove from nodeDelegatorQueue
        nodeDelegatorQueue[ndcIndex] = nodeDelegatorQueue[nodeDelegatorQueue.length - 1];
        nodeDelegatorQueue.pop();

        emit NodeDelegatorRemovedFromQueue(nodeDelegatorAddress);
    }
```

**File:** contracts/LRTDepositPool.sol (L616-624)
```text
    function _checkResidueEthBalance(address nodeDelegatorAddress) internal view {
        if (
            INodeDelegator(nodeDelegatorAddress).getEffectivePodShares() != 0
                || address(nodeDelegatorAddress).balance > maxNegligibleAmount
                || INodeDelegator(nodeDelegatorAddress).getAssetUnstaking(LRTConstants.ETH_TOKEN) > 0
        ) {
            revert NodeDelegatorHasETH();
        }
    }
```

**File:** contracts/LRTDepositPool.sol (L627-645)
```text
    function _checkResidueLSTBalance(address nodeDelegatorAddress) internal view {
        address[] memory supportedAssets = lrtConfig.getSupportedAssetList();
        uint256 supportedAssetsLength = supportedAssets.length;

        uint256 assetBalance;
        for (uint256 i; i < supportedAssetsLength; ++i) {
            if (supportedAssets[i] == LRTConstants.ETH_TOKEN) {
                // this function only checks for residual LST balance
                continue;
            }

            assetBalance = IERC20(supportedAssets[i]).balanceOf(nodeDelegatorAddress)
                + INodeDelegator(nodeDelegatorAddress).getAssetBalance(supportedAssets[i]);
            assetBalance += INodeDelegator(nodeDelegatorAddress).getAssetUnstaking(supportedAssets[i]);

            if (assetBalance > maxNegligibleAmount) {
                revert NodeDelegatorHasAssetBalance(supportedAssets[i], assetBalance);
            }
        }
```
