### Title
`removeSupportedToken` Strict Balance Equality Check Can Be Permanently DOSed by Token Donation - (`contracts/pools/RSETHPoolV3.sol`, `contracts/pools/RSETHPoolV3WithNativeChainBridge.sol`)

---

### Summary

The `removeSupportedToken` function in `RSETHPoolV3.sol` and `RSETHPoolV3WithNativeChainBridge.sol` enforces a strict equality check requiring the pool's token balance to be exactly zero before a token can be removed. Any unprivileged actor can permanently block this administrative operation by donating 1 wei of the target token to the pool contract.

---

### Finding Description

Both pool contracts implement `removeSupportedToken` with the following guard:

```solidity
// RSETHPoolV3.sol line 562
if (IERC20(token).balanceOf(address(this)) != 0) revert TokenBalanceNotZero();
```

```solidity
// RSETHPoolV3WithNativeChainBridge.sol line 609
if (IERC20(token).balanceOf(address(this)) != 0) revert TokenBalanceNotZero();
```

This check requires the pool's balance of the token to be **exactly zero**. Because `IERC20.balanceOf` reflects any tokens held by the contract regardless of how they arrived, an attacker can trivially satisfy the attack condition by transferring 1 wei of the token directly to the pool address at any time — no special permissions required.

The admin (holding `TIMELOCK_ROLE`) cannot atomically drain the balance and call `removeSupportedToken` in a single transaction. Even if the admin first calls `moveAssetsForBridging` (which requires `BRIDGER_ROLE`) to drain the balance, the attacker can immediately re-donate 1 wei in the next block, making the removal permanently unachievable as long as the attacker is willing to spend a negligible amount of tokens. [1](#0-0) [2](#0-1) 

---

### Impact Explanation

The `TIMELOCK_ROLE` holder cannot remove a supported token from the pool. In an emergency scenario — for example, if a supported LST token undergoes a malicious upgrade or becomes insolvent — the protocol's intended response of removing the token to halt further deposits is permanently blocked. Users would continue to be able to deposit the compromised token and receive wrsETH, leading to protocol insolvency or user fund loss. The `pause()` function (requiring `PAUSER_ROLE`) provides a partial mitigation, but it halts the entire pool rather than surgically removing a single token, and the two roles may not be held by the same party.

**Impact: Low** — Contract fails to deliver promised administrative returns (token removal), with potential escalation to fund loss if the pause path is unavailable or insufficient. [3](#0-2) 

---

### Likelihood Explanation

Any holder of 1 wei of a supported token can execute this attack at negligible cost. The attacker does not need to monitor mempool or frontrun a specific transaction — a single donation at any time permanently blocks removal until the attacker stops re-donating. The cost to the attacker is effectively zero (1 wei per block if they choose to maintain the block).

---

### Recommendation

Replace the strict equality check with a pattern that either:

1. **Allows removal regardless of balance**, sweeping any residual balance to a treasury or the caller as part of the removal:
   ```solidity
   uint256 residual = IERC20(token).balanceOf(address(this));
   if (residual > 0) {
       IERC20(token).safeTransfer(treasury, residual);
   }
   ```

2. **Uses a negligible-amount threshold** (consistent with the `maxNegligibleAmount` pattern already used elsewhere in the protocol) rather than requiring exactly zero.

---

### Proof of Concept

1. Admin (TIMELOCK_ROLE) decides to remove token `T` from `RSETHPoolV3` by calling `removeSupportedToken(T, idx)`.
2. Attacker calls `IERC20(T).transfer(address(pool), 1)` — costs 1 wei of `T`.
3. Inside `removeSupportedToken`, `IERC20(T).balanceOf(address(pool))` returns `1 != 0`, triggering `revert TokenBalanceNotZero()`.
4. Admin's transaction reverts. Admin drains balance via `moveAssetsForBridging`.
5. Attacker repeats step 2. The removal is permanently blocked. [1](#0-0) [2](#0-1)

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

**File:** contracts/pools/RSETHPoolV3.sol (L591-596)
```text
    /// @dev Pauses the pausable methods in the contract
    function pause() external onlyRole(PAUSER_ROLE) whenNotPaused {
        paused = true;
        emit Paused(msg.sender);
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
