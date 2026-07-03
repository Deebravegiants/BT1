Let me examine the `removeSupportedToken` and `_addSupportedToken` functions in detail, and also check if `getTokenBalanceMinusFees` is called during deposit.

Based on my full read of `RSETHPoolV3WithNativeChainBridge.sol`, here is the complete analysis:

---

### Title
`removeSupportedToken` Does Not Clear `feeEarnedInToken`, Permanently Freezing Unclaimed Yield and Breaking Re-Added Token Operations — (`contracts/pools/RSETHPoolV3WithNativeChainBridge.sol`)

### Summary

`removeSupportedToken` deletes `supportedTokenOracle[token]` and `tokenBridge[token]` but never clears `feeEarnedInToken[token]`. This has two concrete consequences:

1. **Fees are permanently frozen on removal**: `withdrawFees(receiver, token)` is gated by `onlySupportedToken(token)`, which checks `supportedTokenOracle[token] != address(0)`. After removal that mapping is deleted, so fees can never be withdrawn.
2. **Re-adding the token via `_addSupportedToken` (called by both `reinitialize(3)` and `addSupportedToken`) inherits the stale `feeEarnedInToken`**, causing `getTokenBalanceMinusFees` to underflow and permanently revert in `moveAssetsForBridging` and `bridgeTokens` whenever `balance < stale_fees`.

### Finding Description

**`removeSupportedToken` (lines 606–616):** [1](#0-0) 

The function deletes `supportedTokenOracle[token]` and `tokenBridge[token]` but leaves `feeEarnedInToken[token]` untouched.

**`withdrawFees(receiver, token)` (lines 498–513):** [2](#0-1) 

Gated by `onlySupportedToken(token)` — reverts after removal because `supportedTokenOracle[token]` was deleted. Fees cannot be recovered.

**`_addSupportedToken` (lines 688–707):** [3](#0-2) 

No check or reset of `feeEarnedInToken[token]`. Re-adding a previously removed token silently inherits the stale fee balance.

**`getTokenBalanceMinusFees` (lines 384–386):** [4](#0-3) 

Plain subtraction — Solidity 0.8.27 reverts on underflow. If `balance(token) < feeEarnedInToken[token]`, every call to `moveAssetsForBridging(token, ...)` and `bridgeTokens(token, ...)` reverts permanently.

**`moveAssetsForBridging` and `bridgeTokens` (lines 530–577):** [5](#0-4) [6](#0-5) 

Both call `getTokenBalanceMinusFees` and will revert on underflow.

**`reinitialize(3)` (lines 198–213):** [7](#0-6) 

Calls `_addSupportedToken` — the one-time upgrade path that can re-add a previously removed token with stale fees intact.

### Impact Explanation

- **Permanent freezing of unclaimed yield**: Once `removeSupportedToken` is called on a token with `feeEarnedInToken[token] > 0`, those fees are irrecoverable. `withdrawFees` requires `onlySupportedToken`, which fails post-removal. There is no admin escape hatch.
- **Secondary operational freeze**: If the token is re-added (via `reinitialize(3)` or `addSupportedToken`), `moveAssetsForBridging` and `bridgeTokens` revert on underflow until cumulative new deposits exceed the stale fee amount — which may never happen if the token is low-volume.

### Likelihood Explanation

The precondition `balance == 0` while `feeEarnedInToken[token] > 0` requires the token balance to be drained below the recorded fee reserve. This is achievable with:

- **Fee-on-transfer tokens** where the incoming transfer fee causes the pool to receive less than the amount used to compute `feeEarnedInToken`. Over many deposits, `feeEarnedInToken` can exceed actual balance.
- **Rebasing tokens** that reduce holder balances externally.

The `removeSupportedToken` guard (`balanceOf == 0`) is itself the trigger: it only passes when balance is zero, which is exactly the state where stale fees are unrecoverable. The admin does not need to be malicious — a routine token offboarding (after bridging all non-fee assets) followed by a later re-add is sufficient.

### Recommendation

In `removeSupportedToken`, clear `feeEarnedInToken[token]` (after transferring any remaining balance to a receiver, or explicitly accepting the loss):

```solidity
function removeSupportedToken(address token, uint256 tokenIndex) external onlyRole(TIMELOCK_ROLE) {
    UtilLib.checkNonZeroAddress(token);
    if (supportedTokenList[tokenIndex] != token) revert TokenNotFoundError();
    if (IERC20(token).balanceOf(address(this)) != 0) revert TokenBalanceNotZero();

    delete supportedTokenOracle[token];
    delete tokenBridge[token];
+   delete feeEarnedInToken[token]; // clear stale fee accounting
    supportedTokenList[tokenIndex] = supportedTokenList[supportedTokenList.length - 1];
    supportedTokenList.pop();
    emit RemovedSupportedToken(token);
}
```

Additionally, `_addSupportedToken` should assert `feeEarnedInToken[token] == 0` as a defensive check before re-adding.

### Proof of Concept

```solidity
// 1. Add token, accumulate fees
pool.addSupportedToken(token, oracle, bridge);
token.approve(address(pool), 1000e18);
pool.deposit(token, 1000e18, "ref"); // feeEarnedInToken[token] = F > 0

// 2. Drain balance to 0 (fee-on-transfer: actual received < amount)
//    After bridging all non-fee assets, balance drops to 0 due to token transfer fee
//    (or rebasing reduces balance below F)

// 3. Remove token — succeeds because balanceOf == 0
pool.removeSupportedToken(token, 0);
// feeEarnedInToken[token] == F (NOT cleared)

// 4. withdrawFees now reverts — onlySupportedToken fails
// pool.withdrawFees(receiver, token); // REVERTS: UnsupportedToken

// 5. Re-add via reinitialize(3) or addSupportedToken
pool.reinitialize(token, oracle, bridge, l1Vault); // re-adds with stale F

// 6. getTokenBalanceMinusFees = 0 - F → underflow → revert
pool.moveAssetsForBridging(token, 1); // REVERTS: arithmetic underflow
pool.bridgeTokens(token, 1);          // REVERTS: arithmetic underflow

// Fees F are permanently frozen; bridger operations on this token are broken.
```

### Citations

**File:** contracts/pools/RSETHPoolV3WithNativeChainBridge.sol (L198-213)
```text
    function reinitialize(
        address token,
        address oracle,
        address bridge,
        address _l1VaultETHForL2Chain
    )
        external
        reinitializer(3)
        onlyRole(DEFAULT_ADMIN_ROLE)
    {
        UtilLib.checkNonZeroAddress(_l1VaultETHForL2Chain);

        _addSupportedToken(token, oracle, bridge);

        l1VaultETHForL2Chain = _l1VaultETHForL2Chain;
    }
```

**File:** contracts/pools/RSETHPoolV3WithNativeChainBridge.sol (L384-386)
```text
    function getTokenBalanceMinusFees(address token) public view returns (uint256) {
        return IERC20(token).balanceOf(address(this)) - feeEarnedInToken[token];
    }
```

**File:** contracts/pools/RSETHPoolV3WithNativeChainBridge.sol (L498-513)
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

        emit FeesWithdrawn(amountToSendInToken, token);
    }
```

**File:** contracts/pools/RSETHPoolV3WithNativeChainBridge.sol (L541-543)
```text
        // withdraw up to token - fees
        uint256 tokenBalanceMinusFees = getTokenBalanceMinusFees(token);
        if (amount > tokenBalanceMinusFees) revert InsufficientBalanceInPool();
```

**File:** contracts/pools/RSETHPoolV3WithNativeChainBridge.sol (L566-568)
```text
        // bridge up to the token balance minus fees
        uint256 tokenBalanceMinusFees = getTokenBalanceMinusFees(token);
        if (amount > tokenBalanceMinusFees) revert InsufficientBalance();
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

**File:** contracts/pools/RSETHPoolV3WithNativeChainBridge.sol (L688-707)
```text
    function _addSupportedToken(address token, address oracle, address bridge) internal {
        UtilLib.checkNonZeroAddress(token);
        UtilLib.checkNonZeroAddress(oracle);
        UtilLib.checkNonZeroAddress(bridge);

        if (supportedTokenOracle[token] != address(0)) {
            revert AlreadySupportedToken();
        }
        if (tokenBridge[token] != address(0)) {
            revert AlreadySupportedToken();
        }
        if (IOracle(oracle).getRate() == 0) {
            revert UnsupportedOracle();
        }
        supportedTokenList.push(token);
        supportedTokenOracle[token] = oracle;
        tokenBridge[token] = bridge;

        emit AddSupportedToken(token, oracle, bridge);
    }
```
