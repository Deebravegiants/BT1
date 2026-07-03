### Title
Unbounded Allowance Accumulation in `_unstakeStEth` via `safeIncreaseAllowance` Without Post-Call Reset — (`contracts/unstaking-adapters/UnstakeStETH.sol`)

---

### Summary

`UnstakeStETH._unstakeStEth` uses `safeIncreaseAllowance` to grant the Lido withdrawal queue permission to pull stETH before calling `requestWithdrawals`. Because stETH uses share-based accounting, `transferFrom` inside `requestWithdrawals` may consume slightly less than the approved amount due to integer rounding on shares. The leftover allowance is never reset, so it accumulates with every call. This is the direct analog of the reported `addLiquidity` approval-not-reset pattern.

---

### Finding Description

`_unstakeStEth` in `UnstakeStETH.sol`:

```solidity
function _unstakeStEth(uint256 amountToUnstake) internal {
    stETH.safeIncreaseAllowance(address(withdrawalQueue), amountToUnstake);  // line 49

    uint256[] memory amounts = new uint256[](1);
    amounts[0] = amountToUnstake;

    uint256[] memory requestIds = withdrawalQueue.requestWithdrawals(amounts, address(this));
    ...
}
``` [1](#0-0) 

`safeIncreaseAllowance` adds `amountToUnstake` to the **existing** allowance on every invocation. Lido's `requestWithdrawals` internally calls `stETH.transferFrom(msg.sender, address(this), amount)`. Because stETH balances are derived from shares via integer division, the actual tokens pulled can be 1–2 wei less than `amount`. The residual allowance is never zeroed after the call. Each successive call to `LRTConverter.unstakeStEth` compounds the leftover, causing the `LRTConverter`'s allowance to the Lido withdrawal queue to grow without bound. [2](#0-1) 

The correct pattern — used elsewhere in the same codebase — is `forceApprove(spender, amount)` before the call and `forceApprove(spender, 0)` after, or a single `forceApprove` to the exact amount with a post-call reset.

For comparison, `TokenSwap.depositToKingProtocol` correctly resets approval after the deposit:

```solidity
assetToken.forceApprove(address(kingProtocol), amount);
kingProtocol.deposit(tokens, amounts, address(this));
assetToken.forceApprove(address(kingProtocol), 0);   // reset
``` [3](#0-2) 

---

### Impact Explanation

**Low — Contract fails to deliver promised approval hygiene; no direct value loss under normal conditions.**

The accumulated allowance grants the Lido withdrawal queue an ever-growing right to pull stETH from `LRTConverter`. In normal operation this is harmless because the withdrawal queue only pulls what is requested. However:

1. The contract deviates from the minimal-approval principle it applies everywhere else.
2. If a future upgrade or bug in the Lido withdrawal queue allowed it to pull beyond the requested amount, the inflated allowance would be the enabling condition.
3. The pattern is inconsistent with the rest of the codebase and represents a latent risk surface that grows monotonically with protocol usage.

---

### Likelihood Explanation

**High likelihood of the root cause occurring** (stETH share rounding on every `requestWithdrawals` call leaves 1–2 wei of unused allowance), but **low likelihood of exploitation** under current Lido behaviour. The allowance accumulation is deterministic and observable on-chain.

---

### Recommendation

Replace `safeIncreaseAllowance` with an exact-amount `forceApprove` before the call and a zero-reset `forceApprove` after:

```solidity
function _unstakeStEth(uint256 amountToUnstake) internal {
    stETH.forceApprove(address(withdrawalQueue), amountToUnstake);

    uint256[] memory amounts = new uint256[](1);
    amounts[0] = amountToUnstake;

    uint256[] memory requestIds = withdrawalQueue.requestWithdrawals(amounts, address(this));

    // Reset any dust allowance left by share-rounding
    stETH.forceApprove(address(withdrawalQueue), 0);

    emit UnstakeStETHStarted(requestIds[0]);
}
```

This matches the pattern already used in `TokenSwap.depositToKingProtocol` and `TokenSwap._resetTokenApprovals`. [4](#0-3) 

---

### Proof of Concept

1. Operator calls `LRTConverter.unstakeStEth(1 ether)` → `_unstakeStEth(1e18)` is entered.
2. `safeIncreaseAllowance(withdrawalQueue, 1e18)` sets allowance to `1e18`.
3. `requestWithdrawals([1e18], address(this))` pulls `1e18 - 1 wei` (share rounding).
4. Remaining allowance: `1 wei`.
5. Operator calls `unstakeStEth(1 ether)` again → allowance becomes `1e18 + 1 wei`.
6. After N calls, allowance = `N × 1e18 + (N-1) × dust`, growing without bound.
7. No code path ever resets the allowance to zero after a successful withdrawal request. [5](#0-4)

### Citations

**File:** contracts/unstaking-adapters/UnstakeStETH.sol (L48-57)
```text
    function _unstakeStEth(uint256 amountToUnstake) internal {
        stETH.safeIncreaseAllowance(address(withdrawalQueue), amountToUnstake);

        uint256[] memory amounts = new uint256[](1);
        amounts[0] = amountToUnstake;

        uint256[] memory requestIds = withdrawalQueue.requestWithdrawals(amounts, address(this));

        emit UnstakeStETHStarted(requestIds[0]);
    }
```

**File:** contracts/LRTConverter.sol (L170-177)
```text
    function unstakeStEth(uint256 amountToUnstake)
        external
        nonReentrant
        onlyLRTOperator
        withinUnstakeLimits(amountToUnstake)
    {
        _unstakeStEth(amountToUnstake);
    }
```

**File:** contracts/king-protocol/TokenSwap.sol (L181-187)
```text
        assetToken.forceApprove(address(kingProtocol), amount);

        // Deposit to King Protocol
        kingProtocol.deposit(tokens, amounts, address(this));

        // Reset approval after successful deposit
        assetToken.forceApprove(address(kingProtocol), 0);
```

**File:** contracts/king-protocol/TokenSwap.sol (L264-268)
```text
    function _resetTokenApprovals(address[] memory assets) internal {
        for (uint256 i = 0; i < assets.length; i++) {
            IERC20(assets[i]).forceApprove(address(kingProtocol), 0);
        }
    }
```
