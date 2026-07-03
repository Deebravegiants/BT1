### Title
rsETH Inflation Attack via Direct ETH Donation Inflates `rsETHPrice`, Causing Victim Depositors to Receive Zero rsETH — (File: `contracts/LRTDepositPool.sol`, `contracts/LRTOracle.sol`)

---

### Summary

An unprivileged attacker can donate ETH directly to `LRTDepositPool` and call the public `updateRSETHPrice()` to inflate the stored `rsETHPrice`. Because the rsETH minting formula uses plain integer division (floor), a victim who deposits with `minRSETHAmountExpected = 0` receives **zero rsETH** while their ETH is permanently locked in the protocol. The attacker then redeems their single-wei rsETH position for the entire pool balance, netting the victim's deposit.

---

### Finding Description

**Root cause — minting formula uses floor division with no minimum-share guard**

`LRTDepositPool.getRsETHAmountToMint()` computes:

```solidity
rsethAmountToMint = (amount * lrtOracle.getAssetPrice(asset)) / lrtOracle.rsETHPrice();
``` [1](#0-0) 

If `rsETHPrice` is large enough relative to `amount * assetPrice`, the result floors to **0**. There is no guard that reverts when `rsethAmountToMint == 0`.

**Root cause — `rsETHPrice` is derived from `address(this).balance`, which anyone can inflate**

`LRTOracle._updateRsETHPrice()` computes the new price as:

```solidity
uint256 newRsETHPrice = (totalETHInProtocol - protocolFeeInETH).divWad(rsethSupply);
``` [2](#0-1) 

`totalETHInProtocol` is built by `_getTotalEthInProtocol()`, which calls `getTotalAssetDeposits(ETH_TOKEN)`, which calls `getETHDistributionData()`:

```solidity
ethLyingInDepositPool = address(this).balance;
``` [3](#0-2) 

`LRTDepositPool` has an unrestricted `receive()`:

```solidity
receive() external payable { }
``` [4](#0-3) 

Any address can therefore inflate `totalETHInProtocol` by sending ETH directly to the contract.

**Root cause — `updateRSETHPrice()` is public with no price-increase guard when `pricePercentageLimit == 0`**

```solidity
function updateRSETHPrice() public whenNotPaused {
    _updateRsETHPrice();
}
``` [5](#0-4) 

The price-increase guard only activates when `pricePercentageLimit > 0`:

```solidity
bool isPriceIncreaseOffLimit =
    pricePercentageLimit > 0 && priceDifference > pricePercentageLimit.mulWad(highestRsethPrice);
``` [6](#0-5) 

`pricePercentageLimit` is **not set in `initialize()`**, so it defaults to `0`, leaving the price update completely unrestricted for any caller.

**Victim's slippage parameter does not prevent the attack when set to zero**

`_beforeDeposit` only reverts if `rsethAmountToMint < minRSETHAmountExpected`:

```solidity
if (rsethAmountToMint < minRSETHAmountExpected) {
    revert MinimumAmountToReceiveNotMet();
}
``` [7](#0-6) 

When `minRSETHAmountExpected = 0` (a common default in automated integrations), a `rsethAmountToMint` of `0` passes the check, the deposit succeeds, and the victim receives no rsETH.

---

### Impact Explanation

The victim deposits ETH and receives **0 rsETH**. Because all withdrawal paths (`initiateWithdrawal`, `instantWithdrawal`) require the caller to hold rsETH, the victim has no mechanism to recover their ETH. The funds are **permanently frozen** in the protocol. The attacker recovers their donated ETH plus the victim's deposit by redeeming their single-wei rsETH position at the inflated price.

Impact classification: **Critical — Permanent freezing of user funds / Direct theft of user funds.**

---

### Likelihood Explanation

- `pricePercentageLimit` is `0` by default (not set in `initialize()`), so the price-increase guard is inactive on any freshly deployed or not-yet-configured instance.
- `minAmountToDeposit` is also `0` by default, allowing the attacker's seed deposit of 1 wei.
- Many integrations, scripts, and UI front-ends pass `minRSETHAmountExpected = 0` for simplicity or to avoid reverts.
- The attack is executable atomically in a single block (seed deposit → donate → `updateRSETHPrice()` → victim deposit → `updateRSETHPrice()` → `initiateWithdrawal`).
- The attacker's capital (the donation `D`) is fully recovered after the attack completes.

Likelihood: **Medium** (conditional on `pricePercentageLimit == 0` and victim using zero slippage, both realistic in practice).

---

### Recommendation

1. **Revert on zero rsETH minted**: In `_beforeDeposit`, add `if (rsethAmountToMint == 0) revert ZeroRsETHMinted();` after computing `rsethAmountToMint`.
2. **Set `pricePercentageLimit` in `initialize()`**: A non-zero default (e.g., 1% = `1e16`) prevents a single call from inflating the price by an arbitrary factor.
3. **Restrict `receive()` or account for untracked ETH**: Consider not counting raw `address(this).balance` as protocol TVL, or restricting ETH entry to named functions only.
4. **Virtual offset**: Analogous to the fix in the referenced report, add a virtual offset to the rsETH supply and ETH TVL in the price calculation to make large-scale manipulation economically infeasible.

---

### Proof of Concept

Assume `pricePercentageLimit == 0`, `minAmountToDeposit == 0`, ETH is a supported asset, and `rsETHPrice` has been initialized to `1e18`.

1. **Attacker seeds the pool**: calls `depositETH{value: 1}(0, "")` → receives `1` wei rsETH (formula: `1 * 1e18 / 1e18 = 1`).

2. **Attacker donates**: sends `D = 100 ether` directly to `LRTDepositPool` via `address(depositPool).call{value: 100 ether}("")`.

3. **Attacker inflates price**: calls `lrtOracle.updateRSETHPrice()`.
   - `rsethSupply = 1`, `totalETHInProtocol = 1 + 100e18`
   - `newRsETHPrice = (100e18 + 1) * 1e18 / 1 ≈ 100e18 * 1e18`

4. **Victim deposits**: calls `depositETH{value: 1 ether}(0, "")` with `minRSETHAmountExpected = 0`.
   - `rsethAmountToMint = (1e18 * 1e18) / (100e18 * 1e18) = 0` (floors to zero)
   - Victim receives **0 rsETH**; `1 ether` is now in the pool with no claim.

5. **Attacker updates price again**: calls `lrtOracle.updateRSETHPrice()`.
   - `rsethSupply = 1`, `totalETHInProtocol ≈ 101 ether + 1`
   - `newRsETHPrice ≈ 101e18 * 1e18`

6. **Attacker initiates withdrawal**: calls `withdrawalManager.initiateWithdrawal(ETH_TOKEN, 1, "")`.
   - `expectedAssetAmount = 1 * (101e18 * 1e18) / 1e18 ≈ 101 ether`

7. After the withdrawal delay, attacker calls `completeWithdrawal` and receives `≈ 101 ether`.
   - **Net profit ≈ 1 ether** (victim's deposit), donation of 100 ETH fully recovered.

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
