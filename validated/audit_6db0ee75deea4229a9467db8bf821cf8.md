Audit Report

## Title
Vault Inflation Attack via ETH Donation Inflates `rsETHPrice`, Enabling Zero-rsETH Minting for Victim Deposits — (`contracts/LRTDepositPool.sol`, `contracts/LRTOracle.sol`)

## Summary
An unprivileged attacker can perform a first-depositor inflation attack by donating ETH directly to `LRTDepositPool` (counted in TVL via `address(this).balance`) and calling the public `updateRSETHPrice()`. Because `pricePercentageLimit` is never set in `initialize` and defaults to `0`, the price-increase guard is permanently disabled, allowing `rsETHPrice` to be inflated to an arbitrarily large value in a single call. Subsequent victim deposits with `minRSETHAmountExpected = 0` mint 0 rsETH, permanently absorbing the victim's ETH into the protocol TVL — which the attacker, holding the only rsETH in existence, can later redeem in full.

## Finding Description

**Root cause 1 — `address(this).balance` is used as TVL.**

`getETHDistributionData` reads the raw contract balance:

```solidity
ethLyingInDepositPool = address(this).balance;  // LRTDepositPool.sol L480
```

Because `LRTDepositPool` has an open `receive()`:

```solidity
receive() external payable { }  // LRTDepositPool.sol L58
```

any ETH sent directly to the contract inflates `totalETHInProtocol` without minting any rsETH to the sender.

**Root cause 2 — `pricePercentageLimit` is 0 at deployment.**

`initialize` never sets `pricePercentageLimit`:

```solidity
function initialize(address lrtConfigAddr) external initializer {
    UtilLib.checkNonZeroAddress(lrtConfigAddr);
    lrtConfig = ILRTConfig(lrtConfigAddr);
    emit UpdatedLRTConfig(lrtConfigAddr);
}  // LRTOracle.sol L64-68
```

The price-increase guard short-circuits when the limit is zero:

```solidity
bool isPriceIncreaseOffLimit =
    pricePercentageLimit > 0 && priceDifference > pricePercentageLimit.mulWad(highestRsethPrice);
// LRTOracle.sol L256-257
```

With `pricePercentageLimit == 0`, `isPriceIncreaseOffLimit` is always `false`, so `updateRSETHPrice()` (public, no access control) accepts any price increase:

```solidity
function updateRSETHPrice() public whenNotPaused {
    _updateRsETHPrice();
}  // LRTOracle.sol L87-89
```

**Root cause 3 — Zero rsETH minted is not rejected.**

`_beforeDeposit` only reverts when `rsethAmountToMint < minRSETHAmountExpected`:

```solidity
rsethAmountToMint = getRsETHAmountToMint(asset, depositAmount);
if (rsethAmountToMint < minRSETHAmountExpected) {
    revert MinimumAmountToReceiveNotMet();
}  // LRTDepositPool.sol L665-669
```

When `minRSETHAmountExpected = 0`, the condition `0 < 0` is `false`, so the deposit proceeds and `IRSETH.mint(msg.sender, 0)` is called — a no-op.

**Exploit flow:**

1. Attacker deposits 1 wei ETH → receives 1 wei rsETH (`rsethSupply = 1`, `rsETHPrice = 1e18`).
2. Attacker sends 1000 ETH directly to `LRTDepositPool` via `receive()` → `address(this).balance = 1000e18 + 1`.
3. Attacker calls `updateRSETHPrice()`:
   - `newRsETHPrice = (1000e18 + 1) * 1e18 / 1 ≈ 1000e36`
   - `pricePercentageLimit == 0` → no revert
   - `rsETHPrice` is updated to `~1000e36`
4. Victim calls `depositETH{value: 999 ETH}(0, "")`:
   - `rsethAmountToMint = (999e18 * 1e18) / 1000e36 = 0`
   - `0 < 0` is false → no revert → 0 rsETH minted
   - Victim's 999 ETH is absorbed into TVL
5. Attacker redeems 1 wei rsETH against total TVL of ~1999 ETH, netting ~999 ETH profit.

## Impact Explanation

**Critical — Direct theft of user funds.**

The victim deposits ETH and receives 0 rsETH. Their ETH is permanently absorbed into the protocol TVL. The attacker holds 100% of the rsETH supply and therefore a claim on the entire TVL (their original 1 wei deposit + 1000 ETH donation + victim's 999 ETH). Upon redemption via the withdrawal manager, the attacker recovers the full TVL, stealing the victim's deposit. Net attacker profit equals the victim's deposit minus the 1 wei initial deposit.

## Likelihood Explanation

**Medium-High.** The attack requires no privileged access, no frontrunning, and no flash loans. The attacker only needs to be the first depositor (or reduce supply to 1 wei via deposit + withdrawal), send ETH directly to `LRTDepositPool`, and call the public `updateRSETHPrice()`. The `pricePercentageLimit` protection is absent at deployment, leaving the protocol fully exposed at launch. Callers passing `minRSETHAmountExpected = 0` — the default in many smart contract integrations and scripts — are silently drained with no on-chain error.

## Recommendation

1. **Reject zero rsETH mints** in `_beforeDeposit` (`LRTDepositPool.sol` L665):
   ```solidity
   if (rsethAmountToMint == 0) revert ZeroRsETHMinted();
   ```

2. **Set `pricePercentageLimit` to a non-zero value in `initialize`** (`LRTOracle.sol` L64) so the price-increase guard is active from deployment.

3. **Replace `address(this).balance` with an internal accounting variable** in `getETHDistributionData` (`LRTDepositPool.sol` L480) so direct ETH donations do not inflate TVL.

4. **Perform a sacrificial initial deposit** at deployment — mint a non-trivial amount of rsETH to the zero address (analogous to Uniswap V2's minimum liquidity lock) to make the attack economically infeasible.

## Proof of Concept

```
Initial state: rsETHPrice = 1e18, rsethSupply = 0

1. Attacker calls depositETH{value: 1 wei}(0, ""):
   rsethAmountToMint = (1 * 1e18) / 1e18 = 1 wei rsETH
   → rsethSupply = 1, totalETHInProtocol = 1 wei

2. Attacker sends 1000 ETH directly to LRTDepositPool (via receive()):
   → address(LRTDepositPool).balance = 1000e18 + 1
   → totalETHInProtocol ≈ 1000e18

3. Attacker calls updateRSETHPrice():
   newRsETHPrice = (1000e18 * 1e18) / 1 = 1000e36
   pricePercentageLimit == 0 → isPriceIncreaseOffLimit = false → no revert
   → rsETHPrice = 1000e36

4. Victim calls depositETH{value: 999 ETH}(0, ""):
   rsethAmountToMint = (999e18 * 1e18) / 1000e36 = 0
   0 < 0 is false → no revert → 0 rsETH minted
   → victim's 999 ETH absorbed into TVL

5. Attacker calls updateRSETHPrice():
   totalETHInProtocol ≈ 1999e18, rsethSupply = 1
   rsETHPrice = 1999e36

6. Attacker redeems 1 wei rsETH via LRTWithdrawalManager:
   ETH received ≈ 1999 ETH
   Net profit = 1999 ETH − 1000 ETH − 1 wei = 999 ETH (victim's full deposit)
```

**Foundry test plan:** Deploy `LRTDepositPool` and `LRTOracle` on a local fork with `pricePercentageLimit = 0`. Execute steps 1–6 above as two separate EOAs. Assert that after step 4, victim's rsETH balance is 0 and `address(LRTDepositPool).balance` increased by 999 ETH. Assert that after step 6, attacker's ETH balance increased by approximately 999 ETH. [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3) [5](#0-4) [6](#0-5) [7](#0-6) [8](#0-7)

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

**File:** contracts/LRTDepositPool.sol (L665-669)
```text
        rsethAmountToMint = getRsETHAmountToMint(asset, depositAmount);

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
