### Title
`removeSupportedToken` Permanently Blocked by Dust Token Donation - (`File: contracts/pools/RSETHPoolV3.sol`)

### Summary
The `removeSupportedToken` function in all L2 pool contracts uses a strict `!= 0` equality check on the token's `balanceOf`. Any unprivileged attacker can send a single wei of a supported token directly to the pool contract, permanently preventing the `TIMELOCK_ROLE` from ever removing that token from the supported list.

### Finding Description
In `RSETHPoolV3.sol`, `RSETHPool.sol`, `RSETHPoolNoWrapper.sol`, and `RSETHPoolV3ExternalBridge.sol`, the `removeSupportedToken` function guards removal with:

```solidity
if (IERC20(token).balanceOf(address(this)) != 0) revert TokenBalanceNotZero();
```

This check requires the contract's balance of the token to be **exactly zero** before removal is permitted. Because the pool contracts have no mechanism to reject arbitrary ERC-20 transfers (no `receive`-equivalent for ERC-20), any external actor can call `token.transfer(poolAddress, 1)` to permanently inflate the balance above zero. After this donation, every subsequent call to `removeSupportedToken` for that token will revert with `TokenBalanceNotZero`, regardless of how many legitimate deposits have been bridged out.

The root cause is identical to the M-01 reference: an exact equality check (`!= 0`) on a balance that is externally controllable, instead of a `>=` or "sweep-then-remove" pattern.

### Impact Explanation
The protocol's `TIMELOCK_ROLE` loses the ability to delist any supported LST token from the pool. If a supported token becomes problematic (e.g., a rebasing token breaks fee accounting, or a token's bridge is compromised), the only remaining recourse is to pause the entire pool contract, which also blocks all other depositors. The protocol cannot surgically remove a single token. This maps to **Low — contract fails to deliver promised administrative returns without losing value**.

### Likelihood Explanation
The attack requires only a single ERC-20 `transfer` call of 1 wei to the pool address. No special permissions, no capital at risk for the attacker, and no timing dependency. Any unprivileged address can execute this at any time, including at pool deployment, making it trivially likely if an adversary wishes to lock in a specific token permanently.

### Recommendation
Replace the strict zero-balance guard with a sweep-then-remove pattern, or change the check to allow removal when the only remaining balance is dust not tracked by `feeEarnedInToken`:

```solidity
// Option A: sweep residual balance to treasury before removal
uint256 residual = IERC20(token).balanceOf(address(this));
if (residual > feeEarnedInToken[token]) {
    IERC20(token).safeTransfer(treasury, residual - feeEarnedInToken[token]);
}
// then proceed with removal

// Option B: only block removal if tracked deposits remain
if (getTokenBalanceMinusFees(token) != 0) revert TokenBalanceNotZero();
```

### Proof of Concept

1. Pool is deployed on Optimism/Base/Linea with `wstETH` as a supported token.
2. Attacker calls `wstETH.transfer(poolAddress, 1)` — costs ~1 wei of wstETH.
3. Protocol decides to delist `wstETH` (e.g., due to a bridge issue) and calls `removeSupportedToken(wstETH, 0)`.
4. The check `IERC20(wstETH).balanceOf(address(this)) != 0` evaluates to `true` (balance = 1 wei).
5. Transaction reverts with `TokenBalanceNotZero`. The token is permanently stuck in the supported list.
6. The protocol must pause the entire pool to stop `wstETH` deposits, blocking all other users.

The same pattern exists in all pool variants: [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3)

### Citations

**File:** contracts/pools/RSETHPoolV3.sol (L561-562)
```text
        if (supportedTokenList[tokenIndex] != token) revert TokenNotFoundError();
        if (IERC20(token).balanceOf(address(this)) != 0) revert TokenBalanceNotZero();
```

**File:** contracts/pools/RSETHPool.sol (L662-663)
```text
        if (supportedTokenList[tokenIndex] != token) revert TokenNotFoundError();
        if (IERC20(token).balanceOf(address(this)) != 0) revert TokenBalanceNotZero();
```

**File:** contracts/pools/RSETHPoolNoWrapper.sol (L598-599)
```text
        if (supportedTokenList[tokenIndex] != token) revert TokenNotFoundError();
        if (IERC20(token).balanceOf(address(this)) != 0) revert TokenBalanceNotZero();
```

**File:** contracts/pools/RSETHPoolV3ExternalBridge.sol (L771-772)
```text
        if (supportedTokenList[tokenIndex] != token) revert TokenNotFoundError();
        if (IERC20(token).balanceOf(address(this)) != 0) revert TokenBalanceNotZero();
```
