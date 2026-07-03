### Title
rsETHPrice Reset to 1e18 on Zero Supply Ignores Residual sfrxETH Holdings, Enabling First-Minter Yield Theft — (`contracts/LRTOracle.sol`)

---

### Summary

`LRTOracle._updateRsETHPrice` contains a zero-supply early-return branch that unconditionally resets `rsETHPrice` to `1e18` without inspecting actual protocol holdings. If sfrxETH remains in the protocol (specifically in the `LRTUnstakingVault`, which is counted by `getTotalAssetDeposits`) when `rsethSupply` reaches zero, the first subsequent minter receives rsETH priced at `1e18` while the protocol's backing per rsETH is materially higher, allowing that minter to drain the residual sfrxETH yield.

---

### Finding Description

**Root cause — `LRTOracle._updateRsETHPrice` (lines 218–222):** [1](#0-0) 

```solidity
if (rsethSupply == 0) {
    rsETHPrice = 1 ether;
    highestRsethPrice = 1 ether;
    return;
}
```

The branch returns immediately without calling `_getTotalEthInProtocol()`, so any sfrxETH still tracked by the deposit pool is silently ignored.

**How residual sfrxETH accumulates while rsETH supply drains to zero:**

`LRTWithdrawalManager.initiateWithdrawal` locks in `expectedAssetAmount` at the rsETHPrice prevailing at request time: [2](#0-1) 

`unlockQueue` then burns rsETH and pays out the *minimum* of the locked expectation and the current-price return: [3](#0-2) [4](#0-3) 

Because `SfrxETHPriceOracle.getAssetPrice` always returns the live `pricePerShare`: [5](#0-4) 

…if `rsETHPrice` was stale (lower than actual) when users initiated withdrawals, `currentReturn` at unlock time is *less* than `expectedAssetAmount`, so `payoutAmount = currentReturn < expectedAssetAmount`. The difference — the accumulated sfrxETH yield — is **not** moved out of the unstaking vault. After all rsETH is burned, this residual sfrxETH remains in the vault and is still counted by `getTotalAssetDeposits`: [6](#0-5) 

**First-minter exploitation:**

`getRsETHAmountToMint` divides by the stored `rsETHPrice`: [7](#0-6) 

With `rsETHPrice = 1e18` (reset by the zero-supply branch) and `sfrxETH.pricePerShare() = 1.1e18`, a depositor of `D` sfrxETH receives `D × 1.1e18 / 1e18 = 1.1D` rsETH. Their rsETH now represents *all* protocol holdings — their `D` sfrxETH plus the residual `R` sfrxETH — so after `updateRSETHPrice` is called, `rsETHPrice = (D + R) × 1.1e18 / (1.1D)`. The depositor can withdraw `(D + R)` sfrxETH, extracting `R` sfrxETH they did not deposit.

---

### Impact Explanation

The attacker extracts sfrxETH yield that accumulated while the protocol was running and that was not distributed to the withdrawing users (because those users locked in a lower expected amount). This is a direct, quantifiable theft of unclaimed yield from the protocol. The stolen amount equals the residual sfrxETH left in the unstaking vault after the final `unlockQueue` call.

**Impact: High — Theft of unclaimed yield.**

---

### Likelihood Explanation

The precondition — `rsethSupply` reaching exactly zero while sfrxETH remains in the unstaking vault — requires a complete protocol wind-down combined with a timing gap between withdrawal initiation (stale `rsETHPrice`) and `unlockQueue` execution (live `assetPrice`). This is an uncommon but non-negligible operational state: sfrxETH yield accrues continuously, `rsETHPrice` is only updated on explicit calls, and the minimum-payout logic in `_calculatePayoutAmount` structurally produces a residual whenever `assetPrice` rises between initiation and unlock. A complete wind-down (e.g., migration, emergency shutdown) is a realistic lifecycle event.

**Likelihood: Low.**

---

### Recommendation

Replace the unconditional early return with a branch that still computes the actual backing ratio when protocol holdings are non-zero:

```solidity
if (rsethSupply == 0) {
    uint256 totalETH = _getTotalEthInProtocol();
    if (totalETH == 0) {
        rsETHPrice = 1 ether;
        highestRsethPrice = 1 ether;
    }
    // If totalETH > 0 with zero supply, price is undefined;
    // revert or leave rsETHPrice unchanged to block new mints
    // until the residual is swept or redistributed.
    return;
}
```

Additionally, consider adding a guard in `depositAsset` / `depositETH` that reverts when `rsethSupply == 0` but `_getTotalEthInProtocol() > 0`, preventing any mint until the residual is explicitly resolved by governance.

---

### Proof of Concept

```
State setup (local fork / unit test):
  sfrxETH.pricePerShare = 1.1e18
  Protocol holds 10 sfrxETH in LRTUnstakingVault (residual after wind-down)
  rsETH.totalSupply() == 0

Step 1: call LRTOracle.updateRSETHPrice()
  → rsETHPrice = 1e18, highestRsethPrice = 1e18  (zero-supply branch fires)

Step 2: attacker calls LRTDepositPool.depositAsset(sfrxETH, 1e18, 0, "")
  → rsethAmountToMint = 1e18 * 1.1e18 / 1e18 = 1.1e18 rsETH minted
  → protocol now holds 11 sfrxETH total, rsETHSupply = 1.1e18

Step 3: call LRTOracle.updateRSETHPrice()
  → totalETHInProtocol = 11 * 1.1e18 = 12.1e18
  → newRsETHPrice = 12.1e18 / 1.1e18 = 11e18

Step 4: attacker initiates withdrawal for 1.1e18 rsETH
  → expectedAssetAmount = 1.1e18 * 11e18 / 1.1e18 = 11 sfrxETH

Assert: attacker deposited 1 sfrxETH (1.1 ETH value), withdraws 11 sfrxETH (12.1 ETH value).
Invariant broken: first minter extracted 10 sfrxETH of residual yield they did not deposit.
```

### Citations

**File:** contracts/LRTOracle.sol (L218-222)
```text
        if (rsethSupply == 0) {
            rsETHPrice = 1 ether;
            highestRsethPrice = 1 ether;
            return;
        }
```

**File:** contracts/LRTWithdrawalManager.sol (L168-173)
```text
        uint256 expectedAssetAmount = getExpectedAssetAmount(asset, rsETHUnstaked);

        if (expectedAssetAmount > getAvailableAssetAmount(asset)) revert ExceedAmountToWithdraw();

        // preventing over-withdrawal.
        assetsCommitted[asset] += expectedAssetAmount;
```

**File:** contracts/LRTWithdrawalManager.sol (L798-808)
```text
            uint256 payoutAmount = _calculatePayoutAmount(request, rsETHPrice, assetPrice);

            if (availableAssetAmount < payoutAmount) break; // Exit if not enough assets to cover this request

            assetsCommitted[asset] -= request.expectedAssetAmount;
            // Set the amount the user will receive
            request.expectedAssetAmount = payoutAmount;
            rsETHAmountToBurn += request.rsETHUnstaked;
            availableAssetAmount -= payoutAmount;
            assetAmountToUnlock += payoutAmount;

```

**File:** contracts/LRTWithdrawalManager.sol (L824-835)
```text
    function _calculatePayoutAmount(
        WithdrawalRequest storage request,
        uint256 rsETHPrice,
        uint256 assetPrice
    )
        private
        view
        returns (uint256)
    {
        uint256 currentReturn = (request.rsETHUnstaked * rsETHPrice) / assetPrice;
        return (request.expectedAssetAmount < currentReturn) ? request.expectedAssetAmount : currentReturn;
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

**File:** contracts/LRTDepositPool.sol (L458-461)
```text
        address lrtUnstakingVault = lrtConfig.getContract(LRTConstants.LRT_UNSTAKING_VAULT);

        assetLyingInConverter = 0; // assets in converter are accounted in their eth value => getETHDistributionData()
        assetLyingUnstakingVault = IERC20(asset).balanceOf(lrtUnstakingVault);
```

**File:** contracts/LRTDepositPool.sol (L519-521)
```text
        // calculate rseth amount to mint based on asset amount and asset exchange rate
        rsethAmountToMint = (amount * lrtOracle.getAssetPrice(asset)) / lrtOracle.rsETHPrice();
    }
```
