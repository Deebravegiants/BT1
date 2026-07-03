### Title
Griefing Attack Permanently Blocks Token Removal via Strict Balance Check in `removeSupportedToken` - (File: contracts/pools/RSETHPool.sol, contracts/pools/RSETHPoolNoWrapper.sol)

### Summary
The `removeSupportedToken` function in `RSETHPool.sol` and `RSETHPoolNoWrapper.sol` contains a strict `!= 0` balance check that any unprivileged user can permanently trigger by sending 1 wei of a supported token to the pool contract. This permanently prevents the `TIMELOCK_ROLE` from delisting any supported token, blocking emergency response capabilities.

### Finding Description
Both pool contracts enforce the following guard before removing a token from the supported list:

```solidity
if (IERC20(token).balanceOf(address(this)) != 0) revert TokenBalanceNotZero();
```

In `RSETHPool.sol`: [1](#0-0) 

In `RSETHPoolNoWrapper.sol`: [2](#0-1) 

Because ERC20 `transfer()` is permissionless — any holder can push tokens to any address — an attacker can send 1 wei of any supported token directly to the pool contract at any time. Once the pool holds even 1 wei of that token, `removeSupportedToken` will always revert with `TokenBalanceNotZero`, regardless of how many times the admin tries.

The admin's only apparent workaround is to first drain the balance via `moveAssetsForBridging` or `bridgeTokens`, but because `removeSupportedToken` is gated behind a timelock, the attacker has the full timelock delay to observe the pending removal and front-run it by re-donating 1 wei before the timelock executes. This cycle can be repeated indefinitely at negligible cost. [3](#0-2) 

### Impact Explanation
The `TIMELOCK_ROLE` is permanently unable to delist any supported token from the pool. This blocks the protocol's emergency response path: if a supported token's oracle is manipulated or the token itself is upgraded maliciously, the pool will continue accepting deposits of that token and issuing rsETH against it. The direct impact is that the contract fails to deliver its promised administrative guarantee (token removal), without an immediate direct loss of funds. This maps to **Low — contract fails to deliver promised returns, but doesn't lose value**, with escalation risk to higher severity if a secondary token-compromise event occurs while removal is blocked.

### Likelihood Explanation
The attack requires only holding 1 wei of any supported token (e.g., wstETH on Arbitrum) and calling `transfer`. The cost is 1 wei plus gas. Because `removeSupportedToken` is behind a timelock, the attacker has a guaranteed observation window to front-run every removal attempt. Any rsETH holder or pool depositor qualifies as the attacker.

### Recommendation
Remove the strict `!= 0` balance check from `removeSupportedToken`. The intent of the check — preventing accidental loss of in-flight funds — can be preserved by:
1. Allowing removal regardless of balance, and separately requiring the admin to sweep residual balances via an explicit `sweepToken` function before or after removal.
2. Replacing the hard revert with a warning event, leaving the decision to the admin.
3. Alternatively, tracking only protocol-originated balances (deposits + fees) in a storage variable and checking that tracked balance rather than the raw `balanceOf`.

### Proof of Concept
1. Pool has `wstETH` as a supported token with zero balance.
2. Admin queues `removeSupportedToken(wstETH, 0)` through the timelock.
3. During the timelock delay, attacker calls `IERC20(wstETH).transfer(poolAddress, 1)`.
4. Timelock executes `removeSupportedToken(wstETH, 0)`.
5. Check `IERC20(wstETH).balanceOf(address(this)) != 0` evaluates to `true` (balance = 1 wei).
6. Function reverts with `TokenBalanceNotZero`.
7. Admin re-queues removal; attacker repeats step 3 during the next delay window. The token can never be removed. [4](#0-3) [5](#0-4)

### Citations

**File:** contracts/pools/RSETHPool.sol (L660-670)
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

**File:** contracts/pools/RSETHPoolNoWrapper.sol (L416-428)
```text
    function moveAssetsForBridging(address token)
        external
        nonReentrant
        onlySupportedToken(token)
        onlyRole(BRIDGER_ROLE)
    {
        // withdraw token - fees
        uint256 tokenBalanceMinusFees = IERC20(token).balanceOf(address(this)) - feeEarnedInToken[token];

        IERC20(token).safeTransfer(msg.sender, tokenBalanceMinusFees);

        emit AssetsMovedForBridging(tokenBalanceMinusFees, token);
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
