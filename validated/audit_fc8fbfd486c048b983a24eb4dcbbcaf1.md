### Title
Denial of Service on Withdrawal Initiation via Front-Running `assetsCommitted` — (File: `contracts/LRTWithdrawalManager.sol`)

---

### Summary

`LRTWithdrawalManager.initiateWithdrawal()` reverts if the caller's expected asset amount exceeds `getAvailableAssetAmount()`. Because any rsETH holder can call `initiateWithdrawal()` and thereby increase `assetsCommitted[asset]`, a malicious user can front-run a legitimate withdrawal with a dust-sized withdrawal, shrinking the available amount by a small delta and causing the victim's transaction to revert.

---

### Finding Description

`initiateWithdrawal()` enforces a strict ceiling check before queuing a withdrawal request:

```solidity
// LRTWithdrawalManager.sol line 170
if (expectedAssetAmount > getAvailableAssetAmount(asset)) revert ExceedAmountToWithdraw();
```

`getAvailableAssetAmount()` computes:

```solidity
// LRTWithdrawalManager.sol lines 599–602
uint256 totalAssets = lrtDepositPool.getTotalAssetDeposits(asset);
availableAssetAmount = totalAssets > assetsCommitted[asset] ? totalAssets - assetsCommitted[asset] : 0;
```

Every successful call to `initiateWithdrawal()` increases `assetsCommitted[asset]` by the caller's `expectedAssetAmount` (line 173). There is no access control on `initiateWithdrawal()` beyond `whenNotPaused` — any address holding rsETH can call it.

If a victim submits a withdrawal for the full available amount `A`, an attacker who front-runs with a withdrawal of even 1 wei of rsETH (producing a non-zero `expectedAssetAmount`) will reduce the available amount to `A − δ`. The victim's transaction then reverts with `ExceedAmountToWithdraw` because `A > A − δ`.

---

### Impact Explanation

**Medium — Temporary freezing of funds.**

The victim's rsETH is transferred into the contract at line 166 before the check at line 170; because the transaction reverts, the transfer is rolled back and the victim does not lose tokens. However, the victim cannot initiate their intended withdrawal. An attacker who continuously front-runs every retry can indefinitely delay the victim's ability to enter the withdrawal queue, effectively freezing access to the withdrawal path for that user. The victim's only recourse is to submit a withdrawal for a smaller amount than the current available balance, which the attacker can again front-run.

---

### Likelihood Explanation

**Medium.** The attack requires the attacker to hold rsETH and lock it in the withdrawal queue for the withdrawal delay period (~8 days). This is a real cost. However, the attacker's funds are not lost — they are eventually returned as the underlying asset. Any rsETH holder who wishes to grief a specific user (e.g., a competitor or a large withdrawer who would drain available liquidity) has a clear, repeatable mechanism to do so. The mempool is public and the victim's intended withdrawal amount is visible before inclusion.

---

### Recommendation

1. **Cap the withdrawal amount to the available amount instead of reverting.** If `expectedAssetAmount > getAvailableAssetAmount(asset)`, cap the accepted amount to `getAvailableAssetAmount(asset)` and refund the excess rsETH to the caller, rather than reverting the entire transaction.
2. **Alternatively, accept a `minExpectedAssetAmount` slippage parameter** so users can express tolerance for a slightly reduced available amount, similar to a DEX slippage guard.
3. **Move the rsETH transfer after the availability check** so that a revert does not require rolling back a token transfer (gas efficiency and clarity).

---

### Proof of Concept

1. Available asset amount for ETH is `A = 100 ETH` (`totalAssets = 100 ETH`, `assetsCommitted[ETH] = 0`).
2. Victim calls `initiateWithdrawal(ETH, rsETH_equivalent_of_100_ETH, "")` — this transaction enters the mempool.
3. Attacker observes the mempool and calls `initiateWithdrawal(ETH, minRsEthAmountToWithdraw[ETH], "")` with higher gas, committing `δ` ETH (e.g., 0.001 ETH) to `assetsCommitted[ETH]`.
4. Attacker's transaction is mined first. `assetsCommitted[ETH]` is now `0.001 ETH`. `getAvailableAssetAmount(ETH)` returns `99.999 ETH`.
5. Victim's transaction executes: `expectedAssetAmount = 100 ETH > 99.999 ETH = getAvailableAssetAmount(ETH)` → reverts with `ExceedAmountToWithdraw`.
6. Attacker repeats step 3 on every retry, preventing the victim from ever initiating a full withdrawal.

Relevant code: [1](#0-0) [2](#0-1)

### Citations

**File:** contracts/LRTWithdrawalManager.sol (L162-173)
```text
        if (rsETHUnstaked == 0 || rsETHUnstaked < minRsEthAmountToWithdraw[asset]) {
            revert InvalidAmountToWithdraw();
        }

        IERC20(lrtConfig.rsETH()).safeTransferFrom(msg.sender, address(this), rsETHUnstaked);

        uint256 expectedAssetAmount = getExpectedAssetAmount(asset, rsETHUnstaked);

        if (expectedAssetAmount > getAvailableAssetAmount(asset)) revert ExceedAmountToWithdraw();

        // preventing over-withdrawal.
        assetsCommitted[asset] += expectedAssetAmount;
```

**File:** contracts/LRTWithdrawalManager.sol (L599-603)
```text
    function getAvailableAssetAmount(address asset) public view override returns (uint256 availableAssetAmount) {
        ILRTDepositPool lrtDepositPool = ILRTDepositPool(lrtConfig.getContract(LRTConstants.LRT_DEPOSIT_POOL));
        uint256 totalAssets = lrtDepositPool.getTotalAssetDeposits(asset);
        availableAssetAmount = totalAssets > assetsCommitted[asset] ? totalAssets - assetsCommitted[asset] : 0;
    }
```
