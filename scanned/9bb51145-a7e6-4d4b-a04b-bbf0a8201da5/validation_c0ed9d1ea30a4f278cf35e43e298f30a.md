### Title
rsETH Price Inflation Attack via Direct ETH Donation to `LRTDepositPool` - (File: contracts/LRTDepositPool.sol / contracts/LRTOracle.sol)

### Summary
An attacker who is the first depositor (or acts before a victim's deposit) can donate ETH directly to `LRTDepositPool` via its open `receive()` function, then call the permissionless `LRTOracle.updateRSETHPrice()` to inflate the stored `rsETHPrice`. Subsequent depositors receive drastically fewer rsETH tokens due to integer-division rounding, while the attacker's tiny rsETH position now represents a disproportionate share of the pool — enabling direct theft of depositor funds.

---

### Finding Description

**Minting formula** in `LRTDepositPool.getRsETHAmountToMint()`:

```solidity
rsethAmountToMint = (amount * lrtOracle.getAssetPrice(asset)) / lrtOracle.rsETHPrice();
``` [1](#0-0) 

**Price update formula** in `LRTOracle._updateRsETHPrice()`:

```solidity
uint256 newRsETHPrice = (totalETHInProtocol - protocolFeeInETH).divWad(rsethSupply);
``` [2](#0-1) 

**`totalETHInProtocol`** is computed by `_getTotalEthInProtocol()`, which calls `ILRTDepositPool.getTotalAssetDeposits(asset)`. For ETH, this resolves to:

```solidity
ethLyingInDepositPool = address(this).balance;
``` [3](#0-2) 

`address(this).balance` includes **any ETH sent directly to the contract** via its open `receive()` function:

```solidity
receive() external payable { }
``` [4](#0-3) 

**`updateRSETHPrice()` is permissionless:**

```solidity
function updateRSETHPrice() public whenNotPaused {
    _updateRsETHPrice();
}
``` [5](#0-4) 

The only guard against a large price jump is `pricePercentageLimit`, which is **zero by default** (never set in `initialize()`):

```solidity
bool isPriceIncreaseOffLimit =
    pricePercentageLimit > 0 && priceDifference > pricePercentageLimit.mulWad(highestRsethPrice);
``` [6](#0-5) 

When `pricePercentageLimit == 0`, the condition is always `false` and any price jump is accepted from any caller.

---

### Impact Explanation

**Critical — Direct theft of depositor funds.**

The attacker inflates `rsETHPrice` so that a victim's large ETH deposit mints only 1 wei of rsETH (integer division rounds to zero). The attacker's own 1 wei of rsETH then represents 50 % of the total supply, entitling them to half the combined pool — which includes the victim's ETH. The victim recovers only half their deposit.

---

### Likelihood Explanation

**Medium.** The attack is most effective when the protocol is newly deployed or rsETH supply is near zero. The attacker must:
1. Be the first depositor (or front-run the victim's deposit).
2. Donate ETH ≈ equal to the victim's deposit.
3. The victim must call `depositETH` with `minRSETHAmountExpected = 0` (no slippage guard).

All three conditions are realistic: the protocol starts with zero supply, the donation is a standard ETH transfer, and many integrations or naive users omit the slippage parameter.

---

### Recommendation

1. **Track deposited ETH separately** from raw `address(this).balance`. Use an internal accounting variable incremented only by legitimate deposit paths, so direct ETH transfers are not counted in `totalETHInProtocol`.
2. **Set a non-zero `pricePercentageLimit`** at initialization to cap permissionless price updates.
3. **Enforce a meaningful `minAmountToDeposit`** to raise the cost of the seed deposit.
4. **Require `minRSETHAmountExpected > 0`** in `depositETH` / `depositAsset` to force callers to declare slippage tolerance.

---

### Proof of Concept

```
Initial state: rsETHPrice = 1e18, rsethSupply = 0

Step 1 — Alice deposits 1 wei ETH:
  rsethAmountToMint = (1 * 1e18) / 1e18 = 1 wei rsETH
  Pool ETH balance = 1 wei, rsETH supply = 1 wei

Step 2 — Alice sends 10e18 - 1 wei ETH directly to LRTDepositPool (receive()):
  Pool ETH balance = 10e18 wei (10 ETH)

Step 3 — Alice calls LRTOracle.updateRSETHPrice():
  totalETHInProtocol = 10e18
  newRsETHPrice = 10e18 * 1e18 / 1 = 10e36
  rsETHPrice is now 10e36

Step 4 — Bob calls depositETH{value: 19e18}(0, ""):
  rsethAmountToMint = (19e18 * 1e18) / 10e36 = 1 wei rsETH  ← rounding loss
  Pool ETH balance = 29e18 wei (29 ETH), rsETH supply = 2 wei

Step 5 — updateRSETHPrice() called (by anyone):
  newRsETHPrice = 29e18

### Citations

**File:** contracts/LRTDepositPool.sol (L58-58)
```text
    receive() external payable { }
```

**File:** contracts/LRTDepositPool.sol (L480-480)
```text
        ethLyingInDepositPool = address(this).balance;
```

**File:** contracts/LRTDepositPool.sol (L519-521)
```text
        // calculate rseth amount to mint based on asset amount and asset exchange rate
        rsethAmountToMint = (amount * lrtOracle.getAssetPrice(asset)) / lrtOracle.rsETHPrice();
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

**File:** contracts/LRTOracle.sol (L256-257)
```text
            bool isPriceIncreaseOffLimit =
                pricePercentageLimit > 0 && priceDifference > pricePercentageLimit.mulWad(highestRsethPrice);
```
