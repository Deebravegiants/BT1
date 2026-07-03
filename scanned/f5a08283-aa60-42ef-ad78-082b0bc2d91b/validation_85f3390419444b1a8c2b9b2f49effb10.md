### Title
DoS on `removeSupportedToken` via Token Balance Manipulation - (File: `contracts/pools/RSETHPoolV3.sol`)

### Summary
The `removeSupportedToken` function in `RSETHPoolV3` guards removal with a strict zero-balance check. Any unprivileged user can permanently block this governance action by donating even 1 wei of the target token to the contract, because the balance can never be forced to zero against a persistent griefer.

### Finding Description
`removeSupportedToken` contains the following guard:

```solidity
if (IERC20(token).balanceOf(address(this)) != 0) revert TokenBalanceNotZero();
``` [1](#0-0) 

The intent is to ensure no residual token balance exists before delisting a token. However, `balanceOf(address(this))` is a live, externally-influenceable value: any address can call `IERC20(token).transfer(address(pool), 1)` at any time. Because ERC-20 transfers to arbitrary addresses cannot be rejected, the pool has no mechanism to refuse incoming tokens.

The only egress paths for the token are `moveAssetsForBridging` (BRIDGER_ROLE) and `withdrawFees` (BRIDGER_ROLE), both of which drain only up to `balanceOf - feeEarnedInToken`. An attacker can re-donate 1 wei after every drain, keeping the balance perpetually non-zero at negligible cost (gas + 1 wei per round). [2](#0-1) 

### Impact Explanation
The `TIMELOCK_ROLE` holder cannot delist a token regardless of how many times the balance is drained. A token that must be removed urgently (e.g., its oracle is deprecated or the token itself is compromised) remains permanently listed. The pool continues to accept deposits of that token and mint wrsETH against it. The contract fails to deliver the governance capability it promises.

**Impact: Low** — Contract fails to deliver promised returns (token removal), but no direct theft of user funds occurs in isolation; the `pause()` function can halt new deposits as a mitigation.

### Likelihood Explanation
The attack requires no privilege, no profit motive, and costs only gas plus 1 wei per attempt. It can be executed by any EOA or contract that holds the target token. The attacker does not need to monitor the mempool continuously — a single pre-donation before any removal attempt suffices, and the donation can be repeated cheaply.

**Likelihood: Low** — No financial incentive for the attacker; requires deliberate griefing intent.

### Recommendation
Remove the balance-equality guard from `removeSupportedToken` and instead sweep any residual balance to a designated recipient (e.g., treasury) as part of the removal, or allow removal unconditionally and let the bridger recover stranded tokens afterward:

```diff
function removeSupportedToken(address token, uint256 tokenIndex) external onlyRole(TIMELOCK_ROLE) {
    UtilLib.checkNonZeroAddress(token);
    if (supportedTokenList[tokenIndex] != token) revert TokenNotFoundError();
-   if (IERC20(token).balanceOf(address(this)) != 0) revert TokenBalanceNotZero();

+   // Sweep any residual balance to treasury before delisting
+   uint256 residual = IERC20(token).balanceOf(address(this));
+   if (residual > 0) {
+       address treasury = /* protocol treasury address */;
+       IERC20(token).safeTransfer(treasury, residual);
+   }

    delete supportedTokenOracle[token];
    supportedTokenList[tokenIndex] = supportedTokenList[supportedTokenList.length - 1];
    supportedTokenList.pop();
    emit RemovedSupportedToken(token);
}
```

### Proof of Concept
1. Protocol decides to delist token `T` from `RSETHPoolV3`. The bridger drains the balance to 0 via `moveAssetsForBridging`.
2. Attacker calls `IERC20(T).transfer(address(RSETHPoolV3), 1)`.
3. `TIMELOCK_ROLE` calls `removeSupportedToken(T, idx)`.
4. The check `IERC20(T).balanceOf(address(this)) != 0` evaluates to `true` (balance = 1 wei).
5. Transaction reverts with `TokenBalanceNotZero`.
6. Steps 1–5 repeat indefinitely; token `T` can never be removed. [1](#0-0)

### Citations

**File:** contracts/pools/RSETHPoolV3.sol (L496-513)
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
