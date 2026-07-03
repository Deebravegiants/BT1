Looking at the code, I need to verify the key claim: does `ISfrxETH.pricePerShare()` return frxETH/sfrxETH or ETH/sfrxETH?

### Title
`SfrxETHPriceOracle` Returns frxETH/sfrxETH Instead of ETH/sfrxETH, Inflating rsETHPrice on frxETH Depeg — (`contracts/oracles/SfrxETHPriceOracle.sol`)

---

### Summary

`SfrxETHPriceOracle.getAssetPrice` returns `ISfrxETH.pricePerShare()`, which is denominated in **frxETH per sfrxETH** (the ERC4626 vault's underlying asset ratio), not **ETH per sfrxETH**. `LRTOracle._getTotalEthInProtocol` treats this value as an ETH exchange rate. When frxETH trades at a discount to ETH, `totalETHInProtocol` is overcounted, `rsETHPrice` is set above its true ETH backing, and new depositors receive fewer rsETH than they are owed.

---

### Finding Description

The `ISfrxETH` interface NatSpec in `SfrxETHPriceOracle.sol` is self-contradictory:

> "How much frxETH is 1E18 sfrxETH worth. Price is in ETH, not USD"

The first sentence correctly describes the on-chain semantics: `pricePerShare()` on the real sfrxETH ERC4626 vault returns **frxETH per sfrxETH** (the amount of the underlying asset, frxETH, redeemable per share). The second sentence is incorrect — the value is frxETH-denominated, not ETH-denominated. [1](#0-0) 

`getAssetPrice` returns this value directly with no frxETH→ETH conversion: [2](#0-1) 

`_getTotalEthInProtocol` then uses the returned value as an ETH exchange rate: [3](#0-2) 

When frxETH = 1 ETH (peg holds), the error is zero. When frxETH trades at a discount (e.g., 1 frxETH = 0.97 ETH) and `pricePerShare()` returns `1.05e18` (frxETH/sfrxETH), the oracle reports `1.05 ETH/sfrxETH` when the true ETH value is `1.05 × 0.97 = 1.0185 ETH/sfrxETH`. The sfrxETH portion of `totalETHInProtocol` is overcounted by ~3%.

`updateRSETHPrice()` is public and callable by anyone: [4](#0-3) 

The inflated `totalETHInProtocol` flows directly into `rsETHPrice`: [5](#0-4) 

---

### Impact Explanation

When frxETH depegs below ETH, `rsETHPrice` is set above its true ETH backing. Any new depositor who deposits ETH (or another correctly-priced asset) receives `depositAmount / rsETHPrice` rsETH — fewer tokens than they are owed. Existing rsETH holders benefit at new depositors' expense. No funds are lost from the protocol's perspective, but the protocol fails to deliver the promised exchange rate to new depositors.

**Scope match:** Low — Contract fails to deliver promised returns, but doesn't lose value.

---

### Likelihood Explanation

frxETH has historically maintained a close but imperfect peg to ETH. Any deviation (even a few basis points) causes a proportional mispricing. The trigger requires no privileged access — it is a passive condition that activates automatically whenever the frxETH/ETH market rate diverges. The public `updateRSETHPrice()` entry point means any actor (including a bot or MEV searcher) can lock in the inflated price at will during a depeg event.

---

### Recommendation

Replace the direct `pricePerShare()` call with a two-step conversion:

1. Fetch `sfrxETH.pricePerShare()` → frxETH per sfrxETH.
2. Fetch the frxETH/ETH market price from a Chainlink or Curve TWAP oracle.
3. Return `pricePerShare() × frxETH_per_ETH / 1e18`.

This ensures `getAssetPrice` always returns a value denominated in ETH, consistent with the `IPriceFetcher` interface contract and the `_getTotalEthInProtocol` accounting assumption.

---

### Proof of Concept

```solidity
// Fork test (Mainnet fork, no public-mainnet state changes)
// 1. Deploy/use existing SfrxETHPriceOracle pointing at real sfrxETH
// 2. Mock sfrxETH.pricePerShare() to return 1.05e18 (frxETH/sfrxETH)
// 3. Simulate frxETH depeg: true ETH value = 1.05 * 0.97e18 = 1.0185e18 ETH/sfrxETH
// 4. Call LRTOracle.updateRSETHPrice() (public, no role required)
// 5. Assert rsETHPrice > true_backing_price
//    i.e., rsETHPrice reflects 1.05 ETH/sfrxETH instead of 1.0185 ETH/sfrxETH
// 6. Simulate a new ETH deposit; assert received rsETH < expected rsETH
//    (depositor is shortchanged by ~3% of their sfrxETH-backed share)
```

The `pricePercentageLimit` circuit breaker does not protect against this: the inflated price is a gradual, continuous drift proportional to the frxETH discount, not a sudden spike that would trip the threshold check at `LRTOracle.sol` lines 252–266. [6](#0-5)

### Citations

**File:** contracts/oracles/SfrxETHPriceOracle.sol (L8-11)
```text
interface ISfrxETH {
    /// @notice How much frxETH is 1E18 sfrxETH worth. Price is in ETH, not USD
    function pricePerShare() external view returns (uint256);
}
```

**File:** contracts/oracles/SfrxETHPriceOracle.sol (L35-41)
```text
    function getAssetPrice(address asset) external view returns (uint256) {
        if (asset != sfrxETHContractAddress) {
            revert InvalidAsset();
        }

        return ISfrxETH(sfrxETHContractAddress).pricePerShare();
    }
```

**File:** contracts/LRTOracle.sol (L87-89)
```text
    function updateRSETHPrice() public whenNotPaused {
        _updateRsETHPrice();
    }
```

**File:** contracts/LRTOracle.sol (L250-250)
```text
        uint256 newRsETHPrice = (totalETHInProtocol - protocolFeeInETH).divWad(rsethSupply);
```

**File:** contracts/LRTOracle.sol (L252-266)
```text
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
```

**File:** contracts/LRTOracle.sol (L338-344)
```text
            // assetER is in 1e18 precision (1.0 = 1e18)
            uint256 assetER = getAssetPrice(asset);
            // totalAssetAmt is in 1e18 precision (standard token decimals)
            uint256 totalAssetAmt = ILRTDepositPool(lrtDepositPoolAddr).getTotalAssetDeposits(asset);

            totalETHInProtocol += totalAssetAmt.mulWad(assetER);

```
