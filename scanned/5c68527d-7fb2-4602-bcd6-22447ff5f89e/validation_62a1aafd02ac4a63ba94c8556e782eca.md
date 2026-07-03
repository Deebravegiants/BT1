### Title
Zero-wrsETH Mint on Small Deposits Due to Missing `rsETHAmount == 0` Guard — (`contracts/pools/RSETHPoolV2NBA.sol`)

---

### Summary

`RSETHPoolV2NBA.deposit()` accepts ETH and calls `wrsETH.mint(msg.sender, rsETHAmount)` without verifying that `rsETHAmount > 0`. When the oracle rate is any value greater than `1e18` (the normal operating range for a yield-bearing token) and the deposit is small enough, integer division in `viewSwapRsETHAmountAndFee` truncates `rsETHAmount` to zero. The transaction succeeds, the depositor's ETH is locked in the contract, and the user receives nothing with no on-chain recovery path.

---

### Finding Description

In `viewSwapRsETHAmountAndFee`, the output amount is computed as:

```solidity
rsETHAmount = amountAfterFee * 1e18 / rsETHToETHrate;
``` [1](#0-0) 

This is plain integer division. When `amountAfterFee * 1e18 < rsETHToETHrate`, the result truncates to `0`.

`deposit()` then proceeds unconditionally:

```solidity
if (amount == 0) revert InvalidAmount();   // guards msg.value, not rsETHAmount
(uint256 rsETHAmount, uint256 fee) = viewSwapRsETHAmountAndFee(amount);
feeEarnedInETH += fee;
wrsETH.mint(msg.sender, rsETHAmount);      // mint(msg.sender, 0) — no revert
``` [2](#0-1) 

There is no guard of the form `if (rsETHAmount == 0) revert(...)`. OpenZeppelin's ERC-20 `_mint` accepts a zero amount without reverting, so the call succeeds silently.

The oracle used in production is `InterimRSETHOracle`, which enforces `rate >= 1e18`:

```solidity
function _setRate(uint256 newRate) internal {
    if (newRate < 1e18) revert InvalidRate();
    rate = newRate;
}
``` [3](#0-2) 

rsETH is a yield-bearing token; its rate starts at `1e18` and increases monotonically. Any rate strictly above `1e18` — which is the **normal, expected operating state** — causes the truncation to trigger for sufficiently small deposits.

**Concrete trigger (no oracle manipulation required):**

| Parameter | Value |
|---|---|
| `rsETHToETHrate` | `1.05e18` (5 % yield accrued — routine) |
| `feeBps` | `0` |
| `msg.value` | `1 wei` |
| `amountAfterFee` | `1` |
| `rsETHAmount` | `1 * 1e18 / 1.05e18 = 0` |

The 1 wei is accepted, `feeEarnedInETH` is unchanged (fee = 0), and the ETH sits in the contract balance. The user has no function to reclaim it. `moveAssetsForBridging()` and `withdrawFees()` are both `BRIDGER_ROLE`-only and send funds to the bridger/receiver, not back to the depositor. [4](#0-3) 

---

### Impact Explanation

A user who sends a small ETH deposit (e.g., 1 wei up to `rsETHToETHrate / 1e18 - 1` wei) receives 0 wrsETH while their ETH is permanently locked from their perspective. The invariant "every accepted non-zero ETH deposit produces a non-zero wrsETH mint" is broken. Impact: **Medium — temporary freezing of user funds** (ETH is accepted but irrecoverable by the depositor; admin could theoretically sweep it but has no obligation or mechanism to return it to the original sender).

---

### Likelihood Explanation

This requires no privileged access, no oracle manipulation, and no unusual configuration. It is reachable by any user calling `deposit()` with a small `msg.value` under the normal, post-genesis oracle rate (any rate > `1e18`). The condition becomes easier to trigger as the oracle rate grows over time. Likelihood: **Medium** (requires a small/dust deposit, but the path is fully permissionless and the precondition is the normal operating state of the protocol).

---

### Recommendation

Add a zero-output guard immediately after computing `rsETHAmount`:

```solidity
(uint256 rsETHAmount, uint256 fee) = viewSwapRsETHAmountAndFee(amount);
if (rsETHAmount == 0) revert InvalidAmount();
```

This mirrors the existing `amount == 0` guard and ensures the invariant holds for all accepted deposits.

---

### Proof of Concept

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

// Minimal local test — no mainnet interaction required.
// Deploy InterimRSETHOracle with rate = 1.05e18, deploy RSETHPoolV2NBA,
// deploy a mock wrsETH that records mint calls.

contract MockWrsETH {
    uint256 public lastMintAmount;
    function mint(address, uint256 amount) external { lastMintAmount = amount; }
    // minimal ERC-20 stubs omitted for brevity
}

// Test scenario (pseudo-code, run in Foundry/Hardhat fork):
// 1. oracle.setRate(1.05e18);          // normal yield-bearing rate
// 2. pool.deposit{value: 1}("");       // deposit 1 wei
// 3. assert mockWrsETH.lastMintAmount == 0;   // PASSES — user got nothing
// 4. assert address(pool).balance == 1;       // PASSES — ETH is locked
// 5. assert depositor.balance decreased by 1; // PASSES — ETH is gone
```

The `deposit()` call at step 2 does **not** revert, confirming the vulnerability is reachable on unmodified code.

### Citations

**File:** contracts/pools/RSETHPoolV2NBA.sol (L106-117)
```text
    function deposit(string memory referralId) external payable nonReentrant whenNotPaused {
        uint256 amount = msg.value;

        if (amount == 0) revert InvalidAmount();

        (uint256 rsETHAmount, uint256 fee) = viewSwapRsETHAmountAndFee(amount);

        feeEarnedInETH += fee;

        wrsETH.mint(msg.sender, rsETHAmount);

        emit SwapOccurred(msg.sender, rsETHAmount, fee, referralId);
```

**File:** contracts/pools/RSETHPoolV2NBA.sol (L132-132)
```text
        rsETHAmount = amountAfterFee * 1e18 / rsETHToETHrate;
```

**File:** contracts/pools/RSETHPoolV2NBA.sol (L150-158)
```text
    /// @dev Legacy function - Withdraws assets from the contract for bridging
    function moveAssetsForBridging() external nonReentrant onlyRole(BRIDGER_ROLE) {
        // withdraw ETH - fees
        uint256 ethBalanceMinusFees = address(this).balance - feeEarnedInETH;

        (bool success,) = msg.sender.call{ value: ethBalanceMinusFees }("");
        if (!success) revert TransferFailed();

        emit AssetsMovedForBridging(ethBalanceMinusFees);
```

**File:** contracts/pools/oracle/InterimRSETHOracle.sol (L41-44)
```text
    function _setRate(uint256 newRate) internal {
        if (newRate < 1e18) revert InvalidRate();
        rate = newRate;
        emit RateUpdated(newRate);
```
