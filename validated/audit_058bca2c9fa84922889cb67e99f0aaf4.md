### Title
First Depositor rsETH Price Inflation Attack via Direct ETH Donation to LRTDepositPool - (File: contracts/LRTOracle.sol, contracts/LRTDepositPool.sol)

---

### Summary

The rsETH minting formula in `LRTDepositPool` divides by the stored `rsETHPrice` from `LRTOracle`. That price is computed as `totalETHInProtocol / rsethSupply`, where `totalETHInProtocol` includes `address(this).balance` of the deposit pool. Because `LRTDepositPool` has an open `receive()` function, any caller can inflate the numerator without minting rsETH. The public `updateRSETHPrice()` function then commits the inflated price. When `pricePercentageLimit == 0` (the default — it is never set in `initialize()`), there is no cap on the price increase, so a first depositor can replicate the classic ERC4626 inflation attack: deposit 1 wei, donate a large ETH amount, call `updateRSETHPrice()`, and cause every subsequent depositor who passes `minRSETHAmountExpected = 0` to receive zero rsETH while the attacker's single wei of rsETH absorbs the entire donated pool.

---

### Finding Description

**Minting formula** — `LRTDepositPool.getRsETHAmountToMint()`:

```solidity
rsethAmountToMint = (amount * lrtOracle.getAssetPrice(asset)) / lrtOracle.rsETHPrice();
``` [1](#0-0) 

**Price update** — `LRTOracle._updateRsETHPrice()`:

```solidity
uint256 newRsETHPrice = (totalETHInProtocol - protocolFeeInETH).divWad(rsethSupply);
``` [2](#0-1) 

`totalETHInProtocol` is the sum over all supported assets of `getTotalAssetDeposits(asset)`. For ETH, that delegates to `getETHDistributionData()`:

```solidity
ethLyingInDepositPool = address(this).balance;
``` [3](#0-2) 

So any ETH sent directly to `LRTDepositPool` via its open `receive()`:

```solidity
receive() external payable { }
``` [4](#0-3) 

is immediately counted as protocol TVL without minting any rsETH.

**Missing price-increase guard** — The only protection against an unbounded price jump is:

```solidity
bool isPriceIncreaseOffLimit =
    pricePercentageLimit > 0 && priceDifference > pricePercentageLimit.mulWad(highestRsethPrice);
``` [5](#0-4) 

`pricePercentageLimit` is never initialised in `initialize()`:

```solidity
function initialize(address lrtConfigAddr) external initializer {
    UtilLib.checkNonZeroAddress(lrtConfigAddr);
    lrtConfig = ILRTConfig(lrtConfigAddr);
    emit UpdatedLRTConfig(lrtConfigAddr);
}
``` [6](#0-5) 

It therefore defaults to `0`, making `isPriceIncreaseOffLimit` permanently `false` until an admin explicitly calls `setPricePercentageLimit()`. During this window — which includes the entire initial deployment period — the price can be moved to any value by any caller of the public `updateRSETHPrice()`.

**Slippage guard is user-controlled** — `_beforeDeposit` checks:

```solidity
if (rsethAmountToMint < minRSETHAmountExpected) {
    revert MinimumAmountToReceiveNotMet();
}
``` [7](#0-6) 

When `minRSETHAmountExpected = 0` (a common default in integrations and direct calls), a victim receives 0 rsETH with no revert.

---

### Impact Explanation

**Critical — direct theft of user funds.**

After the attack the attacker's single wei of rsETH represents 100 % of the rsETH supply. The victim's ETH is absorbed into the pool and redeemable only by the attacker. The stolen amount equals the victim's full deposit minus the attacker's donation cost, making the attack profitable whenever the victim's deposit exceeds the donation.

---

### Likelihood Explanation

**Medium.**

Three conditions must hold simultaneously:

1. `pricePercentageLimit == 0` — true by default at deployment; requires no special access.
2. The attacker must fund the donation — requires capital, but the donation is recovered via the inflated rsETH position.
3. The victim must pass `minRSETHAmountExpected = 0` — common in direct contract calls, scripts, and many front-end integrations that omit slippage.

Condition 1 is always satisfied at launch. Conditions 2 and 3 are realistic for any well-funded attacker monitoring the mempool.

---

### Recommendation

1. **Set `pricePercentageLimit` in `initialize()`** to a non-zero value (e.g. 1 % = `1e16`) so that no single `updateRSETHPrice()` call can move the price by more than the configured threshold.
2. **Seed the protocol with an initial rsETH mint** (analogous to the "seed deposit" recommended in the original report) so that the rsETH supply is never 1 wei.
3. **Enforce a non-zero `minRSETHAmountExpected`** at the contract level (e.g. require `minRSETHAmountExpected >= 1`) to prevent silent zero-rsETH deposits.
4. Consider excluding unaccounted ETH (ETH sent via `receive()` that was not deposited through `depositETH`) from `totalETHInProtocol` to remove the donation vector entirely.

---

### Proof of Concept

```
Setup: pricePercentageLimit = 0 (default), minAmountToDeposit = 0

Step 1 — Attacker deposits 1 wei ETH:
  depositETH{value: 1}(minRSETHAmountExpected=0, referralId="")
  rsETHPrice = 1e18  →  rsethAmountToMint = (1 * 1e18) / 1e18 = 1
  Attacker holds: 1 wei rsETH

Step 2 — Attacker donates 10 000 ETH directly:
  (bool ok,) = address(lrtDepositPool).call{value: 10_000 ether}("");
  LRTDepositPool.balance = 10_000 ether + 1 wei
  rsETH totalSupply still = 1 wei

Step 3 — Attacker calls updateRSETHPrice():
  totalETHInProtocol ≈ 10_000 ether + 1 wei
  rsethSupply = 1
  newRsETHPrice ≈ (10_000e18 + 1 - fee) / 1 ≈ 10_000 * 1e18
  pricePercentageLimit == 0  →  isPriceIncreaseOffLimit = false  →  no revert
  rsETHPrice = 10_000 * 1e18

Step 4 — Victim deposits 5 000 ETH:
  depositETH{value: 5_000 ether}(minRSETHAmountExpected=0, referralId="")
  rsethAmountToMint = (5_000e18 * 1e18) / (10_000 * 1e18) = 0  (integer division)
  Victim receives 0 rsETH; 5 000 ETH absorbed into pool

Step 5 — Attacker redeems 1 wei rsETH:
  Pool holds ≈ 15 000 ETH; rsETH supply = 1 wei
  Attacker recovers ≈ 15 000 ETH
  Net profit ≈ 5 000 ETH (victim's deposit minus attacker's donation)
```

### Citations

**File:** contracts/LRTDepositPool.sol (L58-58)
```text
    receive() external payable { }
```

**File:** contracts/LRTDepositPool.sol (L480-480)
```text
        ethLyingInDepositPool = address(this).balance;
```

**File:** contracts/LRTDepositPool.sol (L519-520)
```text
        // calculate rseth amount to mint based on asset amount and asset exchange rate
        rsethAmountToMint = (amount * lrtOracle.getAssetPrice(asset)) / lrtOracle.rsETHPrice();
```

**File:** contracts/LRTDepositPool.sol (L667-669)
```text
        if (rsethAmountToMint < minRSETHAmountExpected) {
            revert MinimumAmountToReceiveNotMet();
        }
```

**File:** contracts/LRTOracle.sol (L64-68)
```text
    function initialize(address lrtConfigAddr) external initializer {
        UtilLib.checkNonZeroAddress(lrtConfigAddr);
        lrtConfig = ILRTConfig(lrtConfigAddr);
        emit UpdatedLRTConfig(lrtConfigAddr);
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
