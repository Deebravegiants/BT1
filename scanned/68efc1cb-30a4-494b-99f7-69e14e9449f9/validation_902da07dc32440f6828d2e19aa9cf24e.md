### Title
Permanent DoS on `removeSupportedToken` via Token Donation - (File: contracts/pools/RSETHPoolV3.sol)

### Summary

Multiple L2 pool contracts guard `removeSupportedToken` with an exact-zero balance check: `IERC20(token).balanceOf(address(this)) != 0`. Any unprivileged caller can permanently block this admin function by donating 1 wei of the token directly to the contract, mirroring the H-02 pattern exactly.

### Finding Description

`removeSupportedToken` in `RSETHPoolV3`, `RSETHPoolNoWrapper`, `RSETHPoolV3ExternalBridge`, and `RSETHPoolV3WithNativeChainBridge` all share the same guard:

```solidity
if (IERC20(token).balanceOf(address(this)) != 0) revert TokenBalanceNotZero();
``` [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3) 

The check is intended to ensure no user funds remain before a token is delisted. However, `balanceOf(address(this))` includes any tokens sent directly to the contract, not just those tracked by `feeEarnedInToken`. An attacker can transfer 1 wei of the token directly to the pool at any time, making the balance permanently non-zero and causing every subsequent `removeSupportedToken` call to revert.

The admin's only recourse is to drain the contract via `moveAssetsForBridging` (BRIDGER\_ROLE) and then call `removeSupportedToken` in a later transaction. Because these are separate transactions, the attacker can front-run the second call by re-donating 1 wei, maintaining the DoS indefinitely at negligible cost. [5](#0-4) 

### Impact Explanation

The admin (TIMELOCK\_ROLE) is permanently unable to delist a supported token. If the token's oracle becomes stale or the token itself is compromised, the pool cannot be cleaned up without pausing the entire contract. This causes the contract to fail to deliver its promised administrative functionality. No user funds are directly stolen or frozen by this bug alone, placing it at **Low** severity.

### Likelihood Explanation

Any unprivileged address holding 1 wei of a supported token can trigger this. The cost is negligible and the attack is repeatable. The attacker only needs to monitor the mempool for `removeSupportedToken` calls and re-donate before each one lands.

### Recommendation

Replace the exact-zero balance check with a balance-difference approach, or track donated (unaccounted) tokens separately. For example, record the expected balance after each deposit/withdrawal and compare against it, rather than requiring `balanceOf == 0`:

```solidity
// Instead of:
if (IERC20(token).balanceOf(address(this)) != 0) revert TokenBalanceNotZero();

// Use:
if (feeEarnedInToken[token] != 0) revert TokenBalanceNotZero();
// Then sweep any residual balance to treasury before deletion.
```

### Proof of Concept

1. Admin calls `addSupportedToken(wstETH, oracle, bridge)` on `RSETHPoolV3`.
2. Users deposit wstETH; the pool accumulates a balance.
3. Admin drains the pool via `moveAssetsForBridging(wstETH, balance)` until `balanceOf(pool) == 0`.
4. Admin submits `removeSupportedToken(wstETH, index)`.
5. Attacker front-runs step 4 by calling `wstETH.transfer(pool, 1)`.
6. `removeSupportedToken` reverts with `TokenBalanceNotZero`.
7. Steps 3–6 repeat indefinitely; the token can never be removed. [1](#0-0)

### Citations

**File:** contracts/pools/RSETHPoolV3.sol (L496-514)
```text
    function moveAssetsForBridging(
        address token,
        uint256 amount
    )
        external
        nonReentrant
        onlySupportedToken(token)
        onlyRole(BRIDGER_ROLE)
    {
        if (amount == 0) revert InvalidAmount();

        // withdraw up to token - fees
        uint256 tokenBalanceMinusFees = getTokenBalanceMinusFees(token);
        if (amount > tokenBalanceMinusFees) revert InsufficientBalanceInPool();

        IERC20(token).safeTransfer(msg.sender, amount);

        emit AssetsMovedForBridging(amount, token);
    }
```

**File:** contracts/pools/RSETHPoolV3.sol (L559-568)
```text
    function removeSupportedToken(address token, uint256 tokenIndex) external onlyRole(TIMELOCK_ROLE) {
        UtilLib.checkNonZeroAddress(token);
        if (supportedTokenList[tokenIndex] != token) revert TokenNotFoundError();
        if (IERC20(token).balanceOf(address(this)) != 0) revert TokenBalanceNotZero();

        delete supportedTokenOracle[token];
        supportedTokenList[tokenIndex] = supportedTokenList[supportedTokenList.length - 1];
        supportedTokenList.pop();
        emit RemovedSupportedToken(token);
    }
```

**File:** contracts/pools/RSETHPoolNoWrapper.sol (L596-606)
```text
    function removeSupportedToken(address token, uint256 tokenIndex) external onlyRole(TIMELOCK_ROLE) {
        UtilLib.checkNonZeroAddress(token);
        if (supportedTokenList[tokenIndex] != token) revert TokenNotFoundError();
        if (IERC20(token).balanceOf(address(this)) != 0) revert TokenBalanceNotZero();

        delete supportedTokenOracle[token];
        delete tokenBridge[token];
        supportedTokenList[tokenIndex] = supportedTokenList[supportedTokenList.length - 1];
        supportedTokenList.pop();
        emit RemovedSupportedToken(token);
    }
```

**File:** contracts/pools/RSETHPoolV3ExternalBridge.sol (L769-779)
```text
    function removeSupportedToken(address token, uint256 tokenIndex) external onlyRole(TIMELOCK_ROLE) {
        UtilLib.checkNonZeroAddress(token);
        if (supportedTokenList[tokenIndex] != token) revert TokenNotFoundError();
        if (IERC20(token).balanceOf(address(this)) != 0) revert TokenBalanceNotZero();

        delete supportedTokenOracle[token];
        delete tokenBridge[token];
        supportedTokenList[tokenIndex] = supportedTokenList[supportedTokenList.length - 1];
        supportedTokenList.pop();
        emit RemovedSupportedToken(token);
    }
```

**File:** contracts/pools/RSETHPoolV3WithNativeChainBridge.sol (L606-616)
```text
    function removeSupportedToken(address token, uint256 tokenIndex) external onlyRole(TIMELOCK_ROLE) {
        UtilLib.checkNonZeroAddress(token);
        if (supportedTokenList[tokenIndex] != token) revert TokenNotFoundError();
        if (IERC20(token).balanceOf(address(this)) != 0) revert TokenBalanceNotZero();

        delete supportedTokenOracle[token];
        delete tokenBridge[token];
        supportedTokenList[tokenIndex] = supportedTokenList[supportedTokenList.length - 1];
        supportedTokenList.pop();
        emit RemovedSupportedToken(token);
    }
```
