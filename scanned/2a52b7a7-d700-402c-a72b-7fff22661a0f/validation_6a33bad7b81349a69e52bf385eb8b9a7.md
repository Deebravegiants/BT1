### Title
Attacker Can Permanently DoS `removeSupportedToken` by Sending 1 Wei of Token to Pool Contracts - (File: contracts/pools/RSETHPoolV3.sol, contracts/pools/RSETHPoolNoWrapper.sol, contracts/pools/RSETHPoolV3ExternalBridge.sol)

### Summary
The `removeSupportedToken` function in multiple L2 pool contracts gates token removal on `IERC20(token).balanceOf(address(this)) == 0`. Because ERC20 tokens are freely transferable to any address, any unprivileged user can send 1 wei of a supported token to the pool, permanently preventing the `TIMELOCK_ROLE` from ever removing that token.

### Finding Description
All three pool contracts contain an identical guard in `removeSupportedToken`:

```solidity
// RSETHPoolV3.sol L562, RSETHPoolNoWrapper.sol L599, RSETHPoolV3ExternalBridge.sol L772
if (IERC20(token).balanceOf(address(this)) != 0) revert TokenBalanceNotZero();
```

The intent is to ensure all deposited tokens have been bridged to L1 before the token is delisted. However, `balanceOf(address(this))` reflects the *total* token balance of the contract, including any tokens sent directly by external parties — not just tokens deposited through the protocol's own `deposit()` flow.

Since ERC20 `transfer` is unrestricted, any address can send an arbitrary amount (even 1 wei) of any supported token directly to the pool contract. After such a transfer, `balanceOf(address(this))` is permanently non-zero (unless the bridger happens to bridge exactly that amount), and `removeSupportedToken` will always revert with `TokenBalanceNotZero`.

The root cause is identical to the referenced report: a function reads `balanceOf(address(this))` — which includes externally-injected tokens — to gate a critical operation, rather than reading a protocol-tracked accounting variable.

### Impact Explanation
The `TIMELOCK_ROLE` loses the ability to delist any supported token that has been griefed with a dust transfer. If a supported token is later paused, exploited, or needs emergency deprecation, the protocol cannot remove it from the supported list. Users can continue depositing the problematic token and receiving wrsETH/rsETH in exchange. This is classified as **Low** — the contract fails to deliver its promised governance functionality (token removal), but no user funds are directly stolen or frozen by the attack itself.

### Likelihood Explanation
Extremely high. The attacker needs only to call `IERC20(token).transfer(poolAddress, 1)` — a single transaction costing 1 wei plus gas. No special role, flash loan, or complex setup is required. The attack can be executed at any time, including front-running a legitimate `removeSupportedToken` call.

### Recommendation
Replace the raw `balanceOf` check with a protocol-tracked accounting variable. The pools already track `feeEarnedInToken[token]`; a similar variable (e.g., `depositedTokenBalance[token]`) should be incremented on each `deposit()` call and decremented on each `moveAssetsForBridging()` / `bridgeTokens()` call. The guard should then be:

```solidity
if (depositedTokenBalance[token] != 0) revert TokenBalanceNotZero();
```

This mirrors the fix recommended in the referenced report: use an internally-tracked share/balance variable rather than the raw ERC20 balance of the contract.

### Proof of Concept

**Scenario:**
1. `RSETHPoolV3` (or `RSETHPoolNoWrapper` / `RSETHPoolV3ExternalBridge`) has wstETH as a supported token.
2. The bridger has already moved all deposited wstETH to L1; `getTokenBalanceMinusFees(wstETH)` returns 0.
3. `TIMELOCK_ROLE` attempts to call `removeSupportedToken(wstETH, index)`.
4. Before the tx lands, an attacker calls `wstETH.transfer(address(pool), 1)`.
5. `removeSupportedToken` executes `IERC20(wstETH).balanceOf(address(this))` → returns 1 → reverts `TokenBalanceNotZero`.
6. The token is permanently stuck in the supported list. Every future `removeSupportedToken` attempt can be front-run identically.

**Affected lines:** [1](#0-0) [2](#0-1) [3](#0-2)

### Citations

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
