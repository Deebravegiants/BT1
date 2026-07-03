### Title
Stale Cached `rsETHPrice` Allows Depositors to Mint Excess rsETH, Stealing Accrued Yield from Existing Holders - (File: contracts/LRTDepositPool.sol)

---

### Summary

`LRTDepositPool.getRsETHAmountToMint` uses a stored, lazily-updated `rsETHPrice` from `LRTOracle`. Because rewards accrue continuously but the price is only updated on explicit calls to `updateRSETHPrice()`, a depositor can mint rsETH at a stale (below-true-value) price, capturing yield that rightfully belongs to existing rsETH holders.

---

### Finding Description

`getRsETHAmountToMint` computes the rsETH to mint as:

```solidity
rsethAmountToMint = (amount * lrtOracle.getAssetPrice(asset)) / lrtOracle.rsETHPrice();
``` [1](#0-0) 

`lrtOracle.rsETHPrice()` is a **stored state variable** in `LRTOracle`, not a live computation:

```solidity
uint256 public override rsETHPrice;
``` [2](#0-1) 

It is only updated when `_updateRsETHPrice()` is called, which computes the true price as:

```solidity
uint256 newRsETHPrice = (totalETHInProtocol - protocolFeeInETH).divWad(rsethSupply);
...
rsETHPrice = newRsETHPrice;
``` [3](#0-2) 

Between reward accruals (e.g., ETH staking rewards arriving at the deposit pool or node delegators) and the next explicit call to `updateRSETHPrice()`, the stored `rsETHPrice` is **lower** than the true current price. A depositor who deposits during this window receives:

```
rsethAmountToMint = amount * assetPrice / stalePrice
```

Since `stalePrice < truePrice`, the depositor receives **more rsETH than their deposit is worth at the true exchange rate**. When `updateRSETHPrice()` is subsequently called, the new price is computed over the inflated `rsethSupply`, resulting in a lower price per rsETH than existing holders would have received had the deposit not occurred. The depositor has effectively captured a portion of the accrued yield.

This is the direct analog of the Connext flaw: "addLiquidity converts asset amounts 1:1 to shares, instead of taking the current value of a share into account." Here, the current value of a share (rsETH) is not taken into account because the price is stale.

---

### Impact Explanation

**High — Theft of unclaimed yield.**

Existing rsETH holders continuously accrue yield (EigenLayer restaking rewards, LST appreciation). This yield is reflected in the true `rsETHPrice = totalETHInProtocol / rsethSupply`. A depositor who mints rsETH at the stale lower price captures a fraction of that accrued yield. The dilution is proportional to: `(truePrice - stalePrice) / truePrice × depositAmount`. Over time, or with large deposits, this represents a meaningful transfer of value from existing holders to the depositor.

---

### Likelihood Explanation

**Medium.** The `updateRSETHPrice()` function is publicly callable but is not invoked atomically with deposits. Rewards accrue continuously from EigenLayer strategies and LST appreciation. Any window between reward accrual and price update is exploitable. Additionally, `_updateRsETHPrice()` can revert for non-manager callers if the price increase exceeds `pricePercentageLimit`:

```solidity
if (!IAccessControl(address(lrtConfig)).hasRole(LRTConstants.MANAGER, msg.sender)) {
    revert PriceAboveDailyThreshold();
}
``` [4](#0-3) 

This means that after a large reward event, the price update may be gated to managers only, extending the staleness window and the exploitable period for any depositor.

---

### Recommendation

Compute the rsETH mint amount using a live, on-the-fly price calculation (i.e., `totalETHInProtocol / rsethSupply`) rather than the stored `rsETHPrice`. Alternatively, call `updateRSETHPrice()` atomically at the start of every deposit transaction before computing `getRsETHAmountToMint`, ensuring the price is always fresh at the time of minting.

---

### Proof of Concept

1. Protocol has 1000 ETH in TVL, 1000 rsETH supply → `rsETHPrice = 1.0 ETH` (stored).
2. EigenLayer rewards of 10 ETH accrue → true price is now `1010/1000 = 1.01 ETH`, but `rsETHPrice` is still `1.0 ETH` (stale).
3. Attacker deposits 100 ETH via `depositETH` **before** anyone calls `updateRSETHPrice()`.
4. `getRsETHAmountToMint` computes: `100 * 1e18 / 1.0e18 = 100 rsETH` minted to attacker.
5. True fair amount at `1.01 ETH/rsETH` would be: `100 / 1.01 ≈ 99.01 rsETH`.
6. Attacker received `~0.99 rsETH` excess, worth `~0.99 × 1.01 ETH ≈ 1 ETH` of value stolen from existing holders.
7. `updateRSETHPrice()` is called: new TVL = `1110 ETH`, new supply = `1100 rsETH`, new price = `1110/1100 ≈ 1.009 ETH` instead of the `1.01 ETH` existing holders would have had without the attacker's deposit. [5](#0-4) [6](#0-5)

### Citations

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

**File:** contracts/LRTOracle.sol (L28-28)
```text
    uint256 public override rsETHPrice;
```

**File:** contracts/LRTOracle.sol (L87-88)
```text
    function updateRSETHPrice() public whenNotPaused {
        _updateRsETHPrice();
```

**File:** contracts/LRTOracle.sol (L250-313)
```text
        uint256 newRsETHPrice = (totalETHInProtocol - protocolFeeInETH).divWad(rsethSupply);

        if (newRsETHPrice > highestRsethPrice) {
            // check if the price is above the threshold
            uint256 priceDifference = newRsETHPrice - highestRsethPrice;
            // pricePercentageLimit is in 1e18 precision (100% = 1e18, 1% = 1e16)
            bool isPriceIncreaseOffLimit =
                pricePercentageLimit > 0 && priceDifference > pricePercentageLimit.mulWad(highestRsethPrice);

            // check if the price difference is above the threshold
            if (isPriceIncreaseOffLimit) {
                // if sender has a manager role, this doesn't revert.
                // if not, it reverts as price went above the threshold
                if (!IAccessControl(address(lrtConfig)).hasRole(LRTConstants.MANAGER, msg.sender)) {
                    revert PriceAboveDailyThreshold();
                }
            }
        }

        // downside protection — pause if price drops too far
        if (newRsETHPrice < highestRsethPrice) {
            uint256 diff = highestRsethPrice - newRsETHPrice;
            // normalizing to 1e18
            bool isPriceDecreaseOffLimit =
                pricePercentageLimit > 0 && diff > pricePercentageLimit.mulWad(highestRsethPrice);

            // if price decrease is off limit, pause the protocol (unless it's already paused)
            if (isPriceDecreaseOffLimit) {
                if (!lrtDepositPool.paused()) lrtDepositPool.pause();
                if (!withdrawalManager.paused()) withdrawalManager.pause();
                _pause();
                return;
            }

            // if price has decreased compared to the previous price, emit an event to reflect that
            if (previousPrice > newRsETHPrice) {
                emit RsETHPriceDecrease(newRsETHPrice, previousPrice);
            }

            // emit an event to notify that the price is currently below the peak (all time high) price
            emit RsETHPriceBelowPeak(highestRsethPrice, newRsETHPrice);
        }

        // update highest price if new price exceeds it
        if (newRsETHPrice > highestRsethPrice) {
            highestRsethPrice = newRsETHPrice;
        }

        // mint protocol fee as rsETH if there's a fee to take
        if (protocolFeeInETH > 0) {
            // Calculate rsETH amount to mint as protocol fee
            uint256 rsethAmountToMintAsProtocolFee = protocolFeeInETH.divWad(newRsETHPrice);

            _checkAndUpdateDailyFeeMintLimit(rsethAmountToMintAsProtocolFee);
            if (rsethAmountToMintAsProtocolFee > 0) {
                address treasury = lrtConfig.getContract(LRTConstants.PROTOCOL_TREASURY);
                IRSETH(rsETHTokenAddress).mint(treasury, rsethAmountToMintAsProtocolFee);
                emit FeeMinted(treasury, rsethAmountToMintAsProtocolFee);
            }
        } else {
            _checkAndUpdateDailyFeeMintLimit(0);
        }

        rsETHPrice = newRsETHPrice;
```
