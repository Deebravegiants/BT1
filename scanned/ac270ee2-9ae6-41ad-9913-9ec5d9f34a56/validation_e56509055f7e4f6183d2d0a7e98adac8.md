### Title
Public `updateRSETHPrice()` Enables Deposit/Price-Update/Instant-Withdrawal Sandwich to Steal Yield — (File: `contracts/LRTOracle.sol`)

### Summary
`LRTOracle.updateRSETHPrice()` has no access control and is callable by any address. The stored `rsETHPrice` is a cached value that grows stale as underlying LST assets (stETH, rETH, etc.) silently accrue staking rewards. An attacker can deposit at the stale (lower) price, call `updateRSETHPrice()` to push the stored price to the current (higher) value, and immediately call `instantWithdrawal()` to redeem at the updated price — extracting yield that belongs to existing rsETH holders.

### Finding Description

`LRTOracle.updateRSETHPrice()` is declared `public` with only a `whenNotPaused` guard:

```solidity
function updateRSETHPrice() public whenNotPaused {
    _updateRsETHPrice();
}
``` [1](#0-0) 

The stored `rsETHPrice` is a cached state variable. It is only updated when this function is explicitly called. Between calls, the underlying LSTs (stETH, rETH, sfrxETH, etc.) continuously accrue staking rewards, causing the protocol's actual ETH value to exceed what `rsETHPrice` reflects.

`LRTDepositPool.getRsETHAmountToMint()` uses the **stored** `rsETHPrice` to compute how many rsETH shares to mint:

```solidity
rsethAmountToMint = (amount * lrtOracle.getAssetPrice(asset)) / lrtOracle.rsETHPrice();
``` [2](#0-1) 

When `rsETHPrice` is stale and lower than the actual value, this formula mints **more** rsETH than the depositor is entitled to.

`LRTWithdrawalManager.instantWithdrawal()` computes the payout using the **current** stored `rsETHPrice` at the time of the call via `getExpectedAssetAmount()`:

```solidity
uint256 assetAmountUnlocked = getExpectedAssetAmount(asset, rsETHUnstaked);
``` [3](#0-2) 

```solidity
underlyingToReceive = amount * lrtOracle.rsETHPrice() / lrtOracle.getAssetPrice(asset);
``` [4](#0-3) 

After the attacker calls `updateRSETHPrice()` to push the stored price up to the current live value, `instantWithdrawal()` pays out at the **higher** price.

The `pricePercentageLimit` guard only blocks price increases that exceed the configured threshold; it does not prevent the attack when the limit is unset (`pricePercentageLimit == 0`) or when the accrued yield is within the allowed band. [5](#0-4) 

### Impact Explanation

An attacker who executes the three-step sandwich in a single transaction (or across two consecutive transactions in the same block):

1. **Deposit** at stale low `rsETHPrice` → receives inflated rsETH shares.
2. **Call `updateRSETHPrice()`** → stored price jumps to the current higher value.
3. **Call `instantWithdrawal()`** → redeems inflated rsETH shares at the higher price.

The profit equals `(updatedPrice − stalePrice) × depositAmount / updatedPrice`, which is directly extracted from the yield that should have been distributed to all existing rsETH holders. This constitutes **theft of unclaimed yield** (High impact).

### Likelihood Explanation

- `instantWithdrawal` must be enabled for the target asset (`isInstantWithdrawalEnabled[asset] == true`).
- `rsETHPrice` naturally becomes stale between keeper calls; the longer the gap, the larger the exploitable discrepancy.
- No special privilege is required; any EOA or contract can call `updateRSETHPrice()` and `instantWithdrawal()`.
- The `pricePercentageLimit` partially mitigates large single-step jumps but does not eliminate the attack for small or zero limits.

Likelihood: **Medium**.

### Recommendation

1. Restrict `updateRSETHPrice()` to a trusted keeper role (e.g., `onlyLRTManager` or a dedicated `PRICE_UPDATER_ROLE`), or add a per-block update guard (`lastUpdateBlock == block.number → revert`).
2. Alternatively, compute the rsETH price live (without caching) inside `getRsETHAmountToMint()` and `getExpectedAssetAmount()` so that deposit and withdrawal always use the same consistent price within a single transaction.
3. Ensure `pricePercentageLimit` is always set to a non-zero value to bound the maximum exploitable price jump per update.

### Proof of Concept

```
// Assume rsETHPrice is stale at 1.00 ETH/rsETH; actual value is 1.005 ETH/rsETH
// instantWithdrawal is enabled for stETH

1. attacker.depositAsset(stETH, 1000e18, 0, "")
   // rsethAmountToMint = 1000e18 * 1e18 / 1.000e18 = 1000 rsETH  (inflated)

2. LRTOracle.updateRSETHPrice()
   // rsETHPrice updated to 1.005e18

3. LRTWithdrawalManager.instantWithdrawal(stETH, 1000e18, "")
   // assetAmountUnlocked = 1000e18 * 1.005e18 / 1e18 = 1005 stETH
   // attacker receives 1005 stETH, having deposited 1000 stETH → profit: 5 stETH
```

The 5 stETH profit is yield stolen from existing rsETH holders who had not yet had their price updated.

### Citations

**File:** contracts/LRTOracle.sol (L87-89)
```text
    function updateRSETHPrice() public whenNotPaused {
        _updateRsETHPrice();
    }
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

**File:** contracts/LRTDepositPool.sol (L519-521)
```text
        // calculate rseth amount to mint based on asset amount and asset exchange rate
        rsethAmountToMint = (amount * lrtOracle.getAssetPrice(asset)) / lrtOracle.rsETHPrice();
    }
```

**File:** contracts/LRTWithdrawalManager.sol (L228-229)
```text
        uint256 assetAmountUnlocked = getExpectedAssetAmount(asset, rsETHUnstaked);
        IRSETH(lrtConfig.rsETH()).burnFrom(address(msg.sender), rsETHUnstaked);
```

**File:** contracts/LRTWithdrawalManager.sol (L592-594)
```text
        // calculate underlying asset amount to receive based on rsETH amount and asset exchange rate
        underlyingToReceive = amount * lrtOracle.rsETHPrice() / lrtOracle.getAssetPrice(asset);
    }
```
