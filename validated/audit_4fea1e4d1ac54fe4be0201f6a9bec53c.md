Audit Report

## Title
Stale `rsETHPrice` Denominator in `getRsETHAmountToMint()` Allows Excess rsETH Minting — (`contracts/LRTDepositPool.sol`)

## Summary
`LRTDepositPool.getRsETHAmountToMint()` computes the mint amount using a live Chainlink asset price in the numerator divided by the stored `rsETHPrice` state variable in the denominator. Because deposit functions never refresh `rsETHPrice` before computing the mint amount, any staleness in the stored price causes depositors to receive more rsETH than their contribution warrants, diluting existing holders' accrued yield. The staleness window is worst when the `pricePercentageLimit` gate blocks the public `updateRSETHPrice()` path.

## Finding Description
`LRTOracle` stores `rsETHPrice` as a plain state variable updated only inside `_updateRsETHPrice()`: [1](#0-0) [2](#0-1) 

The two public entry points that trigger this update are `updateRSETHPrice()` and `updateRSETHPriceAsManager()`: [3](#0-2) 

`getRsETHAmountToMint()` divides a live oracle call by the stored state variable: [4](#0-3) 

Neither `depositETH()` nor `depositAsset()` calls `updateRSETHPrice()` before invoking `_beforeDeposit()` → `getRsETHAmountToMint()`: [5](#0-4) [6](#0-5) 

The aggravating condition: when the true price has risen above `pricePercentageLimit` relative to `highestRsethPrice`, the public `updateRSETHPrice()` reverts for any non-manager caller: [7](#0-6) 

During this window `rsETHPrice` is frozen at its old lower value. Any depositor can observe the on-chain `rsETHPrice` versus the live computed price and deposit during the gap, receiving excess rsETH shares.

## Impact Explanation
`rsETHPrice` increases monotonically as staking rewards accrue. A stale (lower) denominator inflates `rsethAmountToMint`:

```
rsethAmountToMint = (amount × freshAssetPrice) / staleRsETHPrice
                                                   ↑ too low → result too high
```

The excess rsETH represents a claim on more ETH than the depositor contributed. When the price is eventually updated, the inflated rsETH supply means each pre-existing holder's share redeems for less ETH than it should — their accrued staking yield is partially transferred to the new depositor. This is **theft of unclaimed yield** from existing rsETH holders.

**Impact: High.**

## Likelihood Explanation
The staleness window exists continuously between any two `updateRSETHPrice()` calls. It is especially wide and exploitable when `pricePercentageLimit` blocks the public update path — a normal operating condition after a period of strong staking rewards. No special privilege is required; any depositor can observe `rsETHPrice` on-chain, compute the live price off-chain, and deposit during the gap. The condition is repeatable and requires no victim mistakes.

**Likelihood: Medium.**

## Recommendation
`getRsETHAmountToMint()` should compute the rsETH price fresh rather than reading the stored state variable. The safest approach is to expose a `view`-only price computation path that calls `_getTotalEthInProtocol()` inline (without writing state), so the denominator always reflects current TVL and supply. Alternatively, `depositETH()` and `depositAsset()` should call `updateRSETHPrice()` atomically before computing the mint amount, with appropriate handling for the manager-gated threshold case (e.g., using the stored price only when the live price is lower, never when it is higher).

## Proof of Concept
1. At time T, `rsETHPrice = 1.05e18`. Staking rewards accrue; true price rises to `1.06e18`.
2. The price increase exceeds `pricePercentageLimit`. Any call to `updateRSETHPrice()` by a non-manager reverts at: [8](#0-7) 
3. `rsETHPrice` remains `1.05e18` on-chain.
4. Attacker calls `depositAsset(stETH, 1e18, 0, "")`. Inside `getRsETHAmountToMint()`:
   - `getAssetPrice(stETH)` → `1.00e18` (live Chainlink)
   - `rsETHPrice()` → `1.05e18` (stale)
   - `rsethAmountToMint = 1e18 × 1e18 / 1.05e18 ≈ 0.9524e18`
   - Correct at true price: `1e18 × 1e18 / 1.06e18 ≈ 0.9434e18`
   - Excess: `≈ 0.009e18` rsETH per stETH deposited
5. Manager eventually calls `updateRSETHPriceAsManager()`: [9](#0-8) 
   Price updates, but the attacker has already minted at the stale rate and holds excess rsETH backed by existing holders' yield.

**Foundry fork test plan**: Fork mainnet, set `rsETHPrice` to a value below the live computed price, confirm `pricePercentageLimit` blocks the public update, call `depositAsset()`, assert `rsethAmountToMint` exceeds `(amount × assetPrice) / liveComputedPrice`, and verify existing holder redemption value decreases after the manager price update.

### Citations

**File:** contracts/LRTOracle.sol (L28-28)
```text
    uint256 public override rsETHPrice;
```

**File:** contracts/LRTOracle.sol (L87-96)
```text
    function updateRSETHPrice() public whenNotPaused {
        _updateRsETHPrice();
    }

    /// @dev update rsETH price as an manager account
    /// @dev main benefit is to be able to update the price in case of the price going above the threshold
    /// @dev only LRT manager is allowed to call this function
    function updateRSETHPriceAsManager() external onlyLRTManager {
        _updateRsETHPrice();
    }
```

**File:** contracts/LRTOracle.sol (L260-265)
```text
            if (isPriceIncreaseOffLimit) {
                // if sender has a manager role, this doesn't revert.
                // if not, it reverts as price went above the threshold
                if (!IAccessControl(address(lrtConfig)).hasRole(LRTConstants.MANAGER, msg.sender)) {
                    revert PriceAboveDailyThreshold();
                }
```

**File:** contracts/LRTOracle.sol (L313-313)
```text
        rsETHPrice = newRsETHPrice;
```

**File:** contracts/LRTDepositPool.sol (L86-88)
```text
        // checks
        uint256 rsethAmountToMint = _beforeDeposit(LRTConstants.ETH_TOKEN, msg.value, minRSETHAmountExpected);

```

**File:** contracts/LRTDepositPool.sol (L110-112)
```text
        // checks
        uint256 rsethAmountToMint = _beforeDeposit(asset, depositAmount, minRSETHAmountExpected);

```

**File:** contracts/LRTDepositPool.sol (L519-520)
```text
        // calculate rseth amount to mint based on asset amount and asset exchange rate
        rsethAmountToMint = (amount * lrtOracle.getAssetPrice(asset)) / lrtOracle.rsETHPrice();
```
