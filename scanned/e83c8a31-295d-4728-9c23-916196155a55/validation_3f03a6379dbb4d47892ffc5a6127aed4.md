### Title
Stale `rsETHPrice` After `LRTOracle` Unpause Leads to Incorrect rsETH Minting for Depositors - (File: contracts/LRTOracle.sol)

---

### Summary

`LRTOracle.unpause()` does not refresh `rsETHPrice` before re-enabling the oracle. After a pause period during which underlying staking rewards accrue, the stored `rsETHPrice` is lower than the true current rate. Any deposit processed before `updateRSETHPrice()` is called post-unpause mints more rsETH than the depositor is entitled to, diluting existing rsETH holders.

---

### Finding Description

`LRTOracle` stores a cached `rsETHPrice` that is updated only when `updateRSETHPrice()` / `updateRSETHPriceAsManager()` is explicitly called. [1](#0-0) 

The oracle can be paused by any account holding `PAUSER_ROLE`: [2](#0-1) 

While paused, `updateRSETHPrice()` is blocked: [3](#0-2) 

Unpausing simply clears the flag without refreshing the price: [4](#0-3) 

`LRTDepositPool.getRsETHAmountToMint()` divides by the cached `rsETHPrice` to determine how many rsETH shares to mint: [5](#0-4) 

There is no check that the oracle price is fresh before minting. If the oracle was paused for a period during which EigenLayer staking rewards accrued (increasing the true rsETH/ETH rate), the cached `rsETHPrice` is lower than reality. Depositors who transact in the window between `unpause()` and the first successful `updateRSETHPrice()` call receive more rsETH shares than they are entitled to.

The same stale value is propagated cross-chain: `RSETHRateProvider.getLatestRate()` reads `ILRTOracle(rsETHPriceOracle).rsETHPrice()` directly: [6](#0-5) 

If `CrossChainRateProvider.updateRate()` is called before `updateRSETHPrice()` is called post-unpause, the stale rate is broadcast to every L2 `CrossChainRateReceiver`, and all L2 pool deposits (`RSETHPoolV3`, `RSETHPoolV3ExternalBridge`, `RSETHPoolV3WithNativeChainBridge`) use it: [7](#0-6) [8](#0-7) 

---

### Impact Explanation

Existing rsETH holders suffer dilution: new depositors receive more shares than the deposited ETH value warrants, effectively capturing a portion of the yield that had accrued to prior holders during the pause. This maps to **High — Theft of unclaimed yield** in the allowed impact scope.

---

### Likelihood Explanation

The `PAUSER_ROLE` is a normal operational role (separate from admin/manager) used for routine maintenance pauses. Staking rewards accrue continuously; any pause lasting more than a few hours creates a meaningful rate gap. The post-unpause window before `updateRSETHPrice()` is called is not enforced to be zero — there is no atomic "unpause-and-refresh" path in the contract. The scenario is therefore a realistic consequence of normal protocol operations, not an edge case requiring adversarial setup.

---

### Recommendation

`LRTOracle.unpause()` should call `_updateRsETHPrice()` (or its manager-privileged variant) before clearing the paused flag, ensuring `rsETHPrice` reflects the current state of the protocol at the moment deposits resume:

```solidity
function unpause() external whenPaused onlyLRTAdmin {
    _updateRsETHPrice(); // refresh before re-enabling
    paused = false;
    emit Unpaused(msg.sender);
}
```

Alternatively, enforce that `updateRSETHPrice()` must be called within the same transaction or block as `unpause()` before any deposit is accepted.

---

### Proof of Concept

1. At block N, `rsETHPrice = 1.10 ETH` per rsETH. PAUSER_ROLE calls `LRTOracle.pause()` for scheduled maintenance.
2. Over the next 48 hours, EigenLayer strategies earn staking rewards. The true rsETH/ETH rate rises to `1.12 ETH`.
3. Admin calls `LRTOracle.unpause()`. `rsETHPrice` remains `1.10`.
4. Before anyone calls `updateRSETHPrice()`, Alice deposits `100 ETH` via `LRTDepositPool.depositETH()`.
5. `getRsETHAmountToMint` computes: `100e18 * 1e18 / 1.10e18 ≈ 90.9 rsETH`. The correct amount at the true rate would be `100e18 / 1.12e18 ≈ 89.3 rsETH`.
6. Alice receives ~1.6 extra rsETH, funded by diluting the shares of all existing holders — capturing yield that accrued during the pause period.
7. Simultaneously, if `CrossChainRateProvider.updateRate()` is called before `updateRSETHPrice()`, the stale `1.10` rate is broadcast to all L2 pools, and the same over-minting occurs for every L2 depositor until the L2 rate is refreshed. [4](#0-3) [9](#0-8) [10](#0-9)

### Citations

**File:** contracts/LRTOracle.sol (L28-28)
```text
    uint256 public override rsETHPrice;
```

**File:** contracts/LRTOracle.sol (L87-89)
```text
    function updateRSETHPrice() public whenNotPaused {
        _updateRsETHPrice();
    }
```

**File:** contracts/LRTOracle.sol (L138-140)
```text
    function pause() external whenNotPaused onlyRole(LRTConstants.PAUSER_ROLE) {
        _pause();
    }
```

**File:** contracts/LRTOracle.sol (L143-146)
```text
    function unpause() external whenPaused onlyLRTAdmin {
        paused = false;
        emit Unpaused(msg.sender);
    }
```

**File:** contracts/LRTDepositPool.sol (L506-521)
```text
    function getRsETHAmountToMint(
        address asset,
        uint256 amount
    )
        public
        view
        override
        returns (uint256 rsethAmountToMint)
    {
        // setup oracle contract
        address lrtOracleAddress = lrtConfig.getContract(LRTConstants.LRT_ORACLE);
        ILRTOracle lrtOracle = ILRTOracle(lrtOracleAddress);

        // calculate rseth amount to mint based on asset amount and asset exchange rate
        rsethAmountToMint = (amount * lrtOracle.getAssetPrice(asset)) / lrtOracle.rsETHPrice();
    }
```

**File:** contracts/cross-chain/RSETHRateProvider.sol (L26-28)
```text
    /// @notice Returns the latest rate from the rsETH contract
    function getLatestRate() public view override returns (uint256) {
        return ILRTOracle(rsETHPriceOracle).rsETHPrice();
```

**File:** contracts/pools/RSETHPoolV3.sol (L234-237)
```text
    /// @dev Gets the rate from the rsETHOracle
    function getRate() public view returns (uint256) {
        return IOracle(rsETHOracle).getRate();
    }
```

**File:** contracts/pools/RSETHPoolV3.sol (L303-307)
```text
        // rate of rsETH in ETH
        uint256 rsETHToETHrate = getRate();

        // Calculate the final rsETH amount
        rsETHAmount = amountAfterFee * 1e18 / rsETHToETHrate;
```
