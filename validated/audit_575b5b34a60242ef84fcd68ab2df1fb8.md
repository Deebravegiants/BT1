### Title
Rebasing Token Negative Rebase Causes Permanent Arithmetic Underflow in `getTokenBalanceMinusFees`, Freezing All Token Collateral — (`contracts/pools/RSETHPool.sol`)

---

### Summary

`getTokenBalanceMinusFees` performs an unchecked subtraction `balanceOf(pool) - feeEarnedInToken[token]` in Solidity 0.8.x. If a supported token undergoes a negative rebase that reduces the pool's balance below the accumulated `feeEarnedInToken[token]`, every call to `getTokenBalanceMinusFees` reverts with an arithmetic underflow. Because both `bridgeTokens` and `moveAssetsForBridging(address,uint256)` call this function unconditionally before any transfer, all token collateral — including the fee portion — is permanently frozen with no on-chain recovery path.

---

### Finding Description

**Root cause — unchecked subtraction:** [1](#0-0) 

```solidity
function getTokenBalanceMinusFees(address token) public view returns (uint256) {
    return IERC20(token).balanceOf(address(this)) - feeEarnedInToken[token];
}
```

Solidity 0.8 makes this subtraction checked by default. There is no `unchecked` block and no guard ensuring `balanceOf >= feeEarnedInToken[token]` before the subtraction.

**Fee accumulation path:**

Every token deposit increments `feeEarnedInToken[token]` by the fee portion of the deposited amount: [2](#0-1) 

After sufficient deposits, `feeEarnedInToken[token]` is a non-trivial positive value permanently stored in contract state.

**Bridging functions call `getTokenBalanceMinusFees` unconditionally:**

`bridgeTokens`: [3](#0-2) 

`moveAssetsForBridging(address,uint256)`: [4](#0-3) 

Both functions call `getTokenBalanceMinusFees` as their first meaningful operation. If that call reverts, neither function can proceed.

**`withdrawFees` also fails after a severe rebase:** [5](#0-4) 

`withdrawFees(address,address)` attempts `safeTransfer(receiver, feeEarnedInToken[token])`. If the pool's actual balance is below `feeEarnedInToken[token]` (due to the rebase), this transfer also reverts. There is no recovery mechanism.

**`addSupportedToken` imposes no rebasing-token restriction:** [6](#0-5) 

The only checks are non-zero addresses and a non-zero oracle rate. Any ERC-20 token — including rebasing tokens — can be added.

---

### Impact Explanation

Once `balanceOf(pool) < feeEarnedInToken[token]`:

- `getTokenBalanceMinusFees` reverts on every call.
- `bridgeTokens` is permanently bricked for that token.
- `moveAssetsForBridging(address,uint256)` is permanently bricked for that token.
- `withdrawFees(address,address)` also reverts because the pool cannot transfer `feeEarnedInToken[token]` tokens it no longer holds.
- All token collateral held in the pool — both the user-deposited principal and the fee portion — is permanently frozen with no on-chain escape hatch.

This matches **Critical — Permanent freezing of funds**.

---

### Likelihood Explanation

The precondition requires:
1. A rebasing token to be added via `addSupportedToken` (requires `TIMELOCK_ROLE` — a legitimate governance action, not a compromise).
2. Sufficient deposits to accumulate a non-zero `feeEarnedInToken[token]`.
3. A negative rebase event that reduces the pool's balance below the accumulated fee.

Currently deployed instances use wstETH (non-rebasing). However, the `addSupportedToken` function imposes no type restriction, and the protocol may legitimately expand to support rebasing LSTs. A negative rebase (e.g., slashing event on a rebasing staking token) is an external but realistic trigger. Likelihood is **low-to-medium** given current token set, but the impact is irreversible once triggered.

---

### Recommendation

1. **Guard the subtraction** in `getTokenBalanceMinusFees` with a `min` or explicit check:
   ```solidity
   function getTokenBalanceMinusFees(address token) public view returns (uint256) {
       uint256 bal = IERC20(token).balanceOf(address(this));
       uint256 fee = feeEarnedInToken[token];
       return bal >= fee ? bal - fee : 0;
   }
   ```
2. **Cap `feeEarnedInToken` on withdrawal** to the actual balance to prevent the fee tracker from exceeding reality.
3. **Document or enforce** that rebasing tokens are not supported, or add an explicit check in `addSupportedToken` (e.g., verify `balanceOf` is stable before and after a dummy transfer).

---

### Proof of Concept

```solidity
// Local Foundry test — no mainnet required
function test_rebaseDownFreezesPool() public {
    // 1. Deploy MockRebasingToken (balanceOf returns a mutable value)
    MockRebasingToken token = new MockRebasingToken();

    // 2. Add as supported token (TIMELOCK_ROLE action)
    vm.prank(timelockAdmin);
    pool.addSupportedToken(address(token), address(mockOracle), address(mockBridge));

    // 3. User deposits 1000 tokens; fee = 10 tokens (1% feeBps)
    token.mint(user, 1000e18);
    vm.prank(user);
    token.approve(address(pool), 1000e18);
    vm.prank(user);
    pool.deposit(address(token), 1000e18, "ref");
    // pool holds 1000e18 tokens, feeEarnedInToken[token] = 10e18

    // 4. Trigger negative rebase: pool balance drops to 5e18 (below fee of 10e18)
    token.setBalanceOf(address(pool), 5e18);

    // 5. bridgeTokens reverts with arithmetic underflow
    vm.prank(bridger);
    vm.expectRevert(); // arithmetic underflow in getTokenBalanceMinusFees
    pool.bridgeTokens(address(token));

    // 6. moveAssetsForBridging also reverts
    vm.prank(bridger);
    vm.expectRevert();
    pool.moveAssetsForBridging(address(token), 1);

    // 7. withdrawFees also reverts (can't transfer 10e18 when balance is 5e18)
    vm.prank(bridger);
    vm.expectRevert();
    pool.withdrawFees(bridger, address(token));
    // All 5e18 remaining tokens are permanently frozen.
}
```

### Citations

**File:** contracts/pools/RSETHPool.sol (L296-304)
```text
        IERC20(token).safeTransferFrom(msg.sender, address(this), amount);

        (uint256 rsETHAmount, uint256 fee) = viewSwapRsETHAmountAndFee(amount, token);

        feeEarnedInToken[token] += fee;

        IERC20(address(wrsETH)).safeTransfer(msg.sender, rsETHAmount);

        emit SwapOccurred(msg.sender, rsETHAmount, fee, referralId); // Add token address?
```

**File:** contracts/pools/RSETHPool.sol (L396-398)
```text
    function getTokenBalanceMinusFees(address token) public view returns (uint256) {
        return IERC20(token).balanceOf(address(this)) - feeEarnedInToken[token];
    }
```

**File:** contracts/pools/RSETHPool.sol (L438-442)
```text
        uint256 amountToSendInToken = feeEarnedInToken[token];
        feeEarnedInToken[token] = 0;
        IERC20(token).safeTransfer(receiver, amountToSendInToken);

        emit FeesWithdrawn(amountToSendInToken, token);
```

**File:** contracts/pools/RSETHPool.sol (L472-473)
```text
        uint256 tokenBalanceMinusFees = getTokenBalanceMinusFees(token);
        if (amount > tokenBalanceMinusFees) revert InsufficientBalanceInPool();
```

**File:** contracts/pools/RSETHPool.sol (L556-560)
```text
        uint256 balance = getTokenBalanceMinusFees(token);

        if (balance == 0) {
            revert ZeroBridgeAmount();
        }
```

**File:** contracts/pools/RSETHPool.sol (L637-656)
```text
    function addSupportedToken(address token, address oracle, address bridge) external onlyRole(TIMELOCK_ROLE) {
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
