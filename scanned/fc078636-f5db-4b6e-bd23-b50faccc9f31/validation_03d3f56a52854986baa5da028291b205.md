### Title
Integer Division Precision Loss in `getRsETHAmountToMint` Causes Depositors to Receive Fewer rsETH Shares Than Entitled - (File: contracts/LRTDepositPool.sol)

### Summary
The `getRsETHAmountToMint` function in `LRTDepositPool.sol` performs integer division before completing all multiplications, causing systematic truncation that results in depositors receiving fewer rsETH shares than they are mathematically entitled to. This is the direct analog of the HackerGold `getPrice` integer-division ordering bug: dividing by `rsETHPrice` before the numerator is fully scaled discards fractional precision on every deposit.

### Finding Description
In `LRTDepositPool.getRsETHAmountToMint`, the minting formula is:

```solidity
rsethAmountToMint = (amount * lrtOracle.getAssetPrice(asset)) / lrtOracle.rsETHPrice();
```

Both `getAssetPrice(asset)` and `rsETHPrice()` are 1e18-scaled values. The formula computes:

```
rsethAmountToMint = (amount × assetPrice) / rsETHPrice
```

Because Solidity integer division truncates, the remainder of `(amount × assetPrice) % rsETHPrice` is silently discarded on every call. The truncation is systematic and always rounds against the depositor (floor division). For small `amount` values relative to `rsETHPrice`, or when `rsETHPrice` is large (as it grows over time with yield accrual), the truncated dust per deposit accumulates as a permanent loss to depositors.

The same structural flaw appears in `LRTWithdrawalManager.getExpectedAssetAmount`:

```solidity
underlyingToReceive = amount * lrtOracle.rsETHPrice() / lrtOracle.getAssetPrice(asset);
```

and in `LRTWithdrawalManager._calculatePayoutAmount`:

```solidity
uint256 currentReturn = (request.rsETHUnstaked * rsETHPrice) / assetPrice;
```

All three perform a single multiply-then-divide with no intermediate scaling guard, meaning the truncated remainder is lost permanently on every operation.

### Impact Explanation
Every depositor receives strictly fewer rsETH shares than their deposited asset value entitles them to. The truncated fractional shares are not minted to anyone — they are simply lost, meaning the depositor's proportional claim on the protocol TVL is permanently reduced by up to `(rsETHPrice - 1) / rsETHPrice` wei per deposit. As `rsETHPrice` grows with yield (it starts at 1e18 and increases), the maximum per-deposit loss grows proportionally. Over many deposits or for large `rsETHPrice` values, this constitutes a systematic, permanent reduction in promised returns to depositors. This maps to the **Low** impact category: "Contract fails to deliver promised returns, but doesn't lose value."

### Likelihood Explanation
This affects every single deposit through `depositAsset` (which calls `getRsETHAmountToMint`) and every withdrawal through `initiateWithdrawal` (which calls `getExpectedAssetAmount`). It is triggered unconditionally by any unprivileged depositor or withdrawer with no special conditions required.

### Recommendation
Reorder arithmetic to multiply before dividing, and consider using a `mulDiv`-style full-precision helper (already available in the repo as `MathUpgradeable.mulDiv`) to avoid intermediate truncation:

```solidity
// Instead of:
rsethAmountToMint = (amount * lrtOracle.getAssetPrice(asset)) / lrtOracle.rsETHPrice();

// Use full-precision mulDiv:
rsethAmountToMint = MathUpgradeable.mulDiv(amount, lrtOracle.getAssetPrice(asset), lrtOracle.rsETHPrice());
```

Apply the same fix to `getExpectedAssetAmount` and `_calculatePayoutAmount` in `LRTWithdrawalManager.sol`.

### Proof of Concept

Assume `rsETHPrice = 1.0005e18` (after some yield accrual) and `assetPrice = 1e18` (ETH).

A depositor sends `amount = 1e15` (0.001 ETH):

```
numerator   = 1e15 * 1e18 = 1e33
denominator = 1.0005e18   = 1_000_500_000_000_000_000

result      = 1e33 / 1_000_500_000_000_000_000
            = 999_500_249_875_062  (truncated)

exact value = 999_500_249_875_062.468...
```

The depositor loses `0.468` wei of rsETH on this single deposit. Across thousands of deposits, or for larger amounts where `(amount * assetPrice) % rsETHPrice` is large, the cumulative loss is material. The depositor's on-chain rsETH balance is permanently less than their proportional entitlement, and the deficit is unrecoverable. [1](#0-0) [2](#0-1) [3](#0-2)

### Citations

**File:** contracts/LRTDepositPool.sol (L519-520)
```text
        // calculate rseth amount to mint based on asset amount and asset exchange rate
        rsethAmountToMint = (amount * lrtOracle.getAssetPrice(asset)) / lrtOracle.rsETHPrice();
```

**File:** contracts/LRTWithdrawalManager.sol (L592-593)
```text
        // calculate underlying asset amount to receive based on rsETH amount and asset exchange rate
        underlyingToReceive = amount * lrtOracle.rsETHPrice() / lrtOracle.getAssetPrice(asset);
```

**File:** contracts/LRTWithdrawalManager.sol (L833-833)
```text
        uint256 currentReturn = (request.rsETHUnstaked * rsETHPrice) / assetPrice;
```
