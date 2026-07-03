### Title
Stale `rsETHPrice` Enables Yield Theft via Deposit Before Public `updateRSETHPrice()` Call - (File: contracts/LRTOracle.sol)

---

### Summary

`LRTOracle.updateRSETHPrice()` is a **public, permissionless** function. The stored `rsETHPrice` state variable is only updated when this function is called. Because deposits in `LRTDepositPool` use the stale stored `rsETHPrice` to calculate how many rsETH shares to mint, an attacker can deposit at the stale (lower) price, then immediately call `updateRSETHPrice()` themselves to realize the accumulated yield increase — effectively stealing yield that belongs to existing rsETH holders.

---

### Finding Description

`LRTOracle._updateRsETHPrice()` computes a new rsETH price by dividing the real-time total ETH in the protocol (aggregated from live Chainlink feeds) by the current rsETH supply, and stores it in `rsETHPrice`. This function is exposed publicly via `updateRSETHPrice()`:

```solidity
// LRTOracle.sol line 87
function updateRSETHPrice() public whenNotPaused {
    _updateRsETHPrice();
}
```

Between calls to `updateRSETHPrice()`, the stored `rsETHPrice` becomes stale while the underlying assets (stETH, ETHx, etc.) continue to accrue yield and their Chainlink prices drift upward. The real TVL grows, but `rsETHPrice` does not reflect this until the next update.

When a user deposits, `LRTDepositPool.getRsETHAmountToMint()` calculates the rsETH to mint using the **stale stored price**:

```solidity
// LRTDepositPool.sol line 520
rsethAmountToMint = (amount * lrtOracle.getAssetPrice(asset)) / lrtOracle.rsETHPrice();
```

`lrtOracle.getAssetPrice(asset)` reads the **live** Chainlink price, but `lrtOracle.rsETHPrice()` returns the **stale** stored value. If `rsETHPrice` is lower than the true current rate (because rewards have accrued since the last update), the denominator is too small and the attacker receives **more rsETH than fair value**.

The attacker then calls `updateRSETHPrice()` themselves to push the price up to its true value. Their over-minted rsETH is now worth more ETH per token, and the dilution is borne by all existing holders.

---

### Impact Explanation

**High — Theft of unclaimed yield.**

Each time the attacker executes this pattern, they extract a portion of the yield that accrued since the last price update. The profit per attack is bounded by the yield accumulated in the interval (typically daily), but the attack is repeatable every update cycle. Existing rsETH holders are diluted: the price increase they were entitled to is partially captured by the attacker's over-minted shares.

---

### Likelihood Explanation

**Medium.**

The attacker does not need to front-run any specific privileged transaction. They only need to:
1. Observe that the live Chainlink asset prices have risen since the last `updateRSETHPrice()` call (fully on-chain, no off-chain data needed).
2. Deposit at the stale price.
3. Call `updateRSETHPrice()` in the same or next block.

No special role, leaked key, or oracle compromise is required. The attack is fully self-contained and repeatable. The only limiting factor is the magnitude of yield accumulated per update interval.

---

### Recommendation

1. **Atomic price update on deposit:** Call `_updateRsETHPrice()` (or enforce that `rsETHPrice` is fresh within a bounded staleness window) at the start of `depositETH` / `depositAsset` before computing `rsethAmountToMint`. This ensures the mint price always reflects the current TVL.

2. **Alternatively, compute rsETH amount from live TVL directly:** Instead of using the stored `rsETHPrice`, compute the mint amount on-the-fly using `_getTotalEthInProtocol()` and `rsETH.totalSupply()` at deposit time, bypassing the stale cache entirely.

3. **Deposit fee or time-weighted entry:** Introduce a small deposit fee or a time-weighted average price mechanism to make the attack economically unattractive.

---

### Proof of Concept

**Setup:** Assume `rsETHPrice = 1.01e18` (last updated 24 hours ago). Since then, stETH/ETH Chainlink rate has increased, so the true rsETH price is now `1.012e18`.

**Attack steps:**

1. Attacker calls `LRTDepositPool.depositETH{value: 100 ether}(0, "")`.
   - `getAssetPrice(ETH_TOKEN)` returns `1e18` (live).
   - `rsETHPrice` returns `1.01e18` (stale).
   - `rsethAmountToMint = 100e18 * 1e18 / 1.01e18 ≈ 99.0099 rsETH` (over-minted vs. fair `98.8142 rsETH` at true price `1.012e18`).

2. Attacker calls `LRTOracle.updateRSETHPrice()`.
   - `rsETHPrice` is updated to `1.012e18` (true value, slightly reduced by the attacker's dilution).

3. Attacker initiates withdrawal / sells rsETH on secondary market at the new higher price.
   - Attacker redeems `≈99.0099 rsETH × 1.012e18 / 1e18 ≈ 100.198 ETH`, profiting `≈0.198 ETH` at the expense of existing holders.

**Key code references:** [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3)

### Citations

**File:** contracts/LRTOracle.sol (L87-89)
```text
    function updateRSETHPrice() public whenNotPaused {
        _updateRsETHPrice();
    }
```

**File:** contracts/LRTOracle.sol (L214-251)
```text
    function _updateRsETHPrice() internal {
        address rsETHTokenAddress = lrtConfig.rsETH();
        uint256 rsethSupply = IRSETH(rsETHTokenAddress).totalSupply();

        if (rsethSupply == 0) {
            rsETHPrice = 1 ether;
            highestRsethPrice = 1 ether;
            return;
        }

        if (highestRsethPrice == 0) {
            highestRsethPrice = rsETHPrice;
        }

        uint256 previousPrice = rsETHPrice;

        // get total ETH in the protocol (normalized to 1e18)
        uint256 totalETHInProtocol = _getTotalEthInProtocol();

        // calculate previousTVL using rsethSupply multiplied by rsETHPrice
        uint256 previousTVL = rsethSupply.mulWad(rsETHPrice);

        IPausable lrtDepositPool = IPausable(lrtConfig.getContract(LRTConstants.LRT_DEPOSIT_POOL));
        IPausable withdrawalManager = IPausable(lrtConfig.getContract(LRTConstants.LRT_WITHDRAW_MANAGER));

        // determine if the protocol is active (not paused)
        bool protocolPaused = lrtDepositPool.paused() || withdrawalManager.paused() || paused;

        // only take fee if TVL increased and protocol is not paused
        uint256 protocolFeeInETH = 0;
        if (!protocolPaused && totalETHInProtocol > previousTVL) {
            uint256 rewardAmount = totalETHInProtocol - previousTVL;
            protocolFeeInETH = (rewardAmount * lrtConfig.protocolFeeInBPS()) / 10_000;
        }

        // compute new rsETH price based on total ETH minus fee
        uint256 newRsETHPrice = (totalETHInProtocol - protocolFeeInETH).divWad(rsethSupply);

```

**File:** contracts/LRTOracle.sol (L331-349)
```text
    function _getTotalEthInProtocol() private view returns (uint256 totalETHInProtocol) {
        address lrtDepositPoolAddr = lrtConfig.getContract(LRTConstants.LRT_DEPOSIT_POOL);
        address[] memory supportedAssets = lrtConfig.getSupportedAssetList();
        uint256 supportedAssetCount = supportedAssets.length;

        for (uint16 assetIdx; assetIdx < supportedAssetCount;) {
            address asset = supportedAssets[assetIdx];
            // assetER is in 1e18 precision (1.0 = 1e18)
            uint256 assetER = getAssetPrice(asset);
            // totalAssetAmt is in 1e18 precision (standard token decimals)
            uint256 totalAssetAmt = ILRTDepositPool(lrtDepositPoolAddr).getTotalAssetDeposits(asset);

            totalETHInProtocol += totalAssetAmt.mulWad(assetER);

            unchecked {
                ++assetIdx;
            }
        }
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
