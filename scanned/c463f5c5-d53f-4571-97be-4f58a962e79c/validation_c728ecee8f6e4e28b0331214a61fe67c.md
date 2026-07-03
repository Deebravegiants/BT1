### Title
`removeSupportedToken` Does Not Clear `feeEarnedInToken`, Permanently Freezing Accumulated Token Fees After Rebasing Token Balance Reaches Zero — (`contracts/pools/RSETHPoolV3WithNativeChainBridge.sol`)

---

### Summary

`removeSupportedToken` guards removal with a `balanceOf == 0` check but never clears `feeEarnedInToken[token]` and never requires it to be zero. For a rebasing or deflationary token whose on-chain balance can be driven to zero by an external event (e.g. a slashing rebase), the guard passes while accumulated fee accounting remains non-zero. After `supportedTokenOracle[token]` is deleted, the `onlySupportedToken` modifier on `withdrawFees(address,address)` permanently reverts, making those fees irrecoverable.

---

### Finding Description

`removeSupportedToken` enforces one invariant before deleting the token's oracle entry:

```solidity
// RSETHPoolV3WithNativeChainBridge.sol L606-615
function removeSupportedToken(address token, uint256 tokenIndex) external onlyRole(TIMELOCK_ROLE) {
    UtilLib.checkNonZeroAddress(token);
    if (supportedTokenList[tokenIndex] != token) revert TokenNotFoundError();
    if (IERC20(token).balanceOf(address(this)) != 0) revert TokenBalanceNotZero();  // ← only check

    delete supportedTokenOracle[token];   // ← oracle deleted; feeEarnedInToken NOT cleared
    delete tokenBridge[token];
    ...
}
``` [1](#0-0) 

The check `balanceOf == 0` is satisfied whenever a rebasing token's pool balance has been wiped by a slashing event, even if `feeEarnedInToken[token]` still records a positive fee balance. The function then deletes `supportedTokenOracle[token]` without touching `feeEarnedInToken[token]`.

`withdrawFees(address,address)` is gated by `onlySupportedToken`:

```solidity
// L498-513
function withdrawFees(address receiver, address token)
    external nonReentrant onlySupportedToken(token) onlyRole(BRIDGER_ROLE)
{
    uint256 amountToSendInToken = feeEarnedInToken[token];
    ...
}
``` [2](#0-1) 

The modifier checks:

```solidity
modifier onlySupportedToken(address token) {
    if (supportedTokenOracle[token] == address(0)) revert UnsupportedToken();
    _;
}
``` [3](#0-2) 

Once `supportedTokenOracle[token]` is deleted, every call to `withdrawFees(receiver, token)` reverts with `UnsupportedToken`. There is no other code path to drain `feeEarnedInToken[token]`. The same pattern exists identically in `RSETHPoolV3.sol`, `RSETHPoolV3ExternalBridge.sol`, and `RSETHPoolNoWrapper.sol`. [4](#0-3) [5](#0-4) 

---

### Impact Explanation

Accumulated protocol fees denominated in the removed token become permanently inaccessible. `feeEarnedInToken[token]` retains its non-zero value in storage but no callable function can read it out. This is **permanent freezing of unclaimed yield** (Medium per the allowed impact scope). The fees are not transferred to an attacker; they are simply locked in the contract forever.

---

### Likelihood Explanation

The precondition requires:
1. A rebasing or deflationary token (e.g. a non-wrapped LST) to be added via `addSupportedToken` — a legitimate TIMELOCK action.
2. A slashing or rebase event to reduce the pool's token balance to exactly zero while `feeEarnedInToken[token] > 0` — realistic for any LST with slashing risk.
3. TIMELOCK to call `removeSupportedToken` in response to the zero-balance state — a natural operational response.

No malicious actor is required. The TIMELOCK acts in good faith; the contract simply lacks the guard `feeEarnedInToken[token] == 0` before allowing removal. Likelihood is low-to-medium (depends on whether a rebasing token is ever added), but the impact is irreversible once triggered.

---

### Recommendation

Add a check in `removeSupportedToken` that prevents removal while unclaimed fees exist, or clear `feeEarnedInToken[token]` (transferring any remaining balance to a designated receiver) before deleting the oracle entry:

```solidity
// Option A: block removal if fees are outstanding
if (feeEarnedInToken[token] != 0) revert UnclaimedFeesExist();

// Option B: sweep fees before removal (if balance permits)
if (feeEarnedInToken[token] != 0) {
    uint256 fees = feeEarnedInToken[token];
    feeEarnedInToken[token] = 0;
    IERC20(token).safeTransfer(feeReceiver, fees);
}
```

Apply the same fix to `RSETHPoolV3.sol`, `RSETHPoolV3ExternalBridge.sol`, and `RSETHPoolNoWrapper.sol`.

---

### Proof of Concept

```solidity
// Local fork / unit test — no mainnet interaction
function test_frozenFees() public {
    // 1. Deploy mock rebasing token; add as supported token via TIMELOCK
    MockRebasingToken token = new MockRebasingToken();
    vm.prank(timelock);
    pool.addSupportedToken(address(token), address(mockOracle), address(mockBridge));

    // 2. User deposits; feeEarnedInToken accumulates
    token.mint(user, 1e18);
    vm.prank(user);
    token.approve(address(pool), 1e18);
    vm.prank(user);
    pool.deposit(address(token), 1e18, "ref");
    assertGt(pool.feeEarnedInToken(address(token)), 0);

    // 3. Slashing rebase wipes pool balance to 0
    token.slash(address(pool), token.balanceOf(address(pool)));
    assertEq(token.balanceOf(address(pool)), 0);

    // 4. TIMELOCK removes token (balanceOf == 0 check passes)
    vm.prank(timelock);
    pool.removeSupportedToken(address(token), 0);

    // 5. withdrawFees now permanently reverts
    vm.prank(bridger);
    vm.expectRevert(RSETHPoolV3WithNativeChainBridge.UnsupportedToken.selector);
    pool.withdrawFees(receiver, address(token));

    // 6. Fees are permanently frozen
    assertGt(pool.feeEarnedInToken(address(token)), 0); // non-zero, inaccessible
}
```

### Citations

**File:** contracts/pools/RSETHPoolV3WithNativeChainBridge.sol (L93-96)
```text
    modifier onlySupportedToken(address token) {
        if (supportedTokenOracle[token] == address(0)) revert UnsupportedToken();
        _;
    }
```

**File:** contracts/pools/RSETHPoolV3WithNativeChainBridge.sol (L498-510)
```text
    function withdrawFees(
        address receiver,
        address token
    )
        external
        nonReentrant
        onlySupportedToken(token)
        onlyRole(BRIDGER_ROLE)
    {
        // withdraw fees in token
        uint256 amountToSendInToken = feeEarnedInToken[token];
        feeEarnedInToken[token] = 0;
        IERC20(token).safeTransfer(receiver, amountToSendInToken);
```

**File:** contracts/pools/RSETHPoolV3WithNativeChainBridge.sol (L606-615)
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
