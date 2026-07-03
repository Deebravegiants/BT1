### Title
rsETH Price Inflation via Unrestricted ETH Donation Enables First-Depositor Fund Theft — (File: `contracts/LRTDepositPool.sol`, `contracts/LRTOracle.sol`)

---

### Summary

An attacker can donate ETH directly to `LRTDepositPool` through its unrestricted `receive()` function, then call the public `updateRSETHPrice()` to inflate the stored `rsETHPrice`. Because `_beforeDeposit()` does not enforce `rsethAmountToMint > 0`, a subsequent depositor who passes `minRSETHAmountExpected = 0` will have their ETH accepted by the protocol while receiving zero rsETH in return. The attacker, holding rsETH from an earlier tiny deposit, recovers the donated ETH plus the victim's ETH upon withdrawal, netting the victim's full deposit.

---

### Finding Description

**Root cause 1 — Unrestricted ETH donation inflates TVL**

`LRTDepositPool` exposes a bare `receive()` function: [1](#0-0) 

ETH sent here is immediately counted in `totalETHInProtocol` because `getETHDistributionData()` reads `address(this).balance`: [2](#0-1) 

**Root cause 2 — Public price update with no default cap**

`updateRSETHPrice()` is callable by anyone: [3](#0-2) 

The price-increase guard is only active when `pricePercentageLimit > 0`, which is **not set during `initialize()`** and therefore defaults to `0`: [4](#0-3) 

With `pricePercentageLimit == 0`, the condition `isPriceIncreaseOffLimit` is always `false`, so any magnitude of price inflation passes unchecked.

**Root cause 3 — No zero-mint guard in `_beforeDeposit`**

`getRsETHAmountToMint` uses integer division: [5](#0-4) 

`_beforeDeposit` only checks `rsethAmountToMint < minRSETHAmountExpected`; it never asserts `rsethAmountToMint > 0`: [6](#0-5) 

When `minRSETHAmountExpected == 0` (the zero-value default), a deposit that computes `rsethAmountToMint = 0` silently succeeds, minting nothing for the depositor.

---

### Impact Explanation

**Critical — Direct theft of user funds.**

Attack math (simplified):

| Step | ETH in pool | rsETH supply | rsETH price |
|---|---|---|---|
| Attacker deposits 1 wei | 1 wei | 1 wei | 1e18 |
| Attacker donates X ETH via `receive()` | 1 wei + X | 1 wei | 1e18 (stale) |
| Attacker calls `updateRSETHPrice()` | 1 wei + X | 1 wei | ≈ X·1e18 |
| Victim deposits Y ETH (Y < X) | 1 wei + X + Y | 1 wei | ≈ X·1e18 |

`rsethAmountToMint = Y·1e18 / (X·1e18) = Y/X` → rounds to **0** when Y < X.

Victim's Y ETH is absorbed into the pool. Attacker redeems their 1 wei rsETH (the only rsETH in existence) and receives the entire pool: `1 wei + X + Y ≈ X + Y`. Net attacker profit: **Y ETH** (the victim's full deposit). The donated X ETH is fully recovered.

---

### Likelihood Explanation

**Medium.**

Two conditions must hold simultaneously:

1. `pricePercentageLimit == 0` — this is the **on-chain default** because `initialize()` never sets it. It remains 0 until an admin explicitly calls `setPricePercentageLimit()`.
2. The victim passes `minRSETHAmountExpected = 0` — common for users interacting directly with the contract, scripted integrations, or frontends that omit slippage protection.

The attack is a classic frontrun: the attacker observes a pending `depositETH` transaction in the mempool, prepends the donation + price update, and the victim's transaction executes at the inflated price. No privileged access is required.

---

### Recommendation

1. **Enforce a non-zero mint amount**: add `if (rsethAmountToMint == 0) revert ZeroRsETHMinted();` inside `_beforeDeposit()`. [7](#0-6) 

2. **Set `pricePercentageLimit` during initialization** to a safe value (e.g., 1 % = `1e16`) so that a single `updateRSETHPrice()` call cannot inflate the price by an arbitrary factor. [8](#0-7) 

3. **Restrict the `receive()` function** to only accept ETH from known, trusted callers (NodeDelegators, reward receivers, etc.) rather than from arbitrary addresses. [1](#0-0) 

---

### Proof of Concept

```
// Precondition: pricePercentageLimit == 0 (default), minAmountToDeposit == 0 (default)

// 1. Attacker deposits 1 wei ETH → receives 1 wei rsETH at price 1e18
lrtDepositPool.depositETH{value: 1}(0, "");

// 2. Attacker donates 10 ETH directly to the deposit pool (no rsETH minted)
(bool ok,) = address(lrtDepositPool).call{value: 10 ether}("");

// 3. Attacker triggers price update — new price ≈ 10e18 (10 ETH / 1 wei rsETH)
//    pricePercentageLimit == 0 → no revert
lrtOracle.updateRSETHPrice();

// 4. Victim deposits 5 ETH with no slippage guard
//    rsethAmountToMint = 5e18 * 1e18 / 10e18 = 0 (integer division)
//    _beforeDeposit: 0 < 0 is false → no revert → victim gets 0 rsETH
lrtDepositPool.depositETH{value: 5 ether}(0, "");

// 5. Attacker later redeems 1 wei rsETH through the withdrawal manager
//    Receives ≈ 10 ETH (donation) + 5 ETH (victim) + 1 wei (own deposit)
//    Net profit: 5 ETH
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

**File:** contracts/LRTDepositPool.sol (L520-520)
```text
        rsethAmountToMint = (amount * lrtOracle.getAssetPrice(asset)) / lrtOracle.rsETHPrice();
```

**File:** contracts/LRTDepositPool.sol (L648-670)
```text
    function _beforeDeposit(
        address asset,
        uint256 depositAmount,
        uint256 minRSETHAmountExpected
    )
        private
        view
        returns (uint256 rsethAmountToMint)
    {
        if (depositAmount == 0 || depositAmount < minAmountToDeposit) {
            revert InvalidAmountToDeposit();
        }

        if (_checkIfDepositAmountExceedesCurrentLimit(asset, depositAmount)) {
            revert MaximumDepositLimitReached();
        }

        rsethAmountToMint = getRsETHAmountToMint(asset, depositAmount);

        if (rsethAmountToMint < minRSETHAmountExpected) {
            revert MinimumAmountToReceiveNotMet();
        }
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

**File:** contracts/LRTOracle.sol (L87-89)
```text
    function updateRSETHPrice() public whenNotPaused {
        _updateRsETHPrice();
    }
```

**File:** contracts/LRTOracle.sol (L256-257)
```text
            bool isPriceIncreaseOffLimit =
                pricePercentageLimit > 0 && priceDifference > pricePercentageLimit.mulWad(highestRsethPrice);
```
