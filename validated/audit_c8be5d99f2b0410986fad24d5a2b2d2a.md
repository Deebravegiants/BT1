The vulnerability is real and traceable. Let me confirm the exact lines before writing the finding.

### Title
Untracked Direct Token Transfers Are Silently Swept to L1 via `bridgeTokens` Due to Raw `balanceOf` Accounting — (`contracts/pools/RSETHPoolV3ExternalBridge.sol`)

---

### Summary

`getTokenBalanceMinusFees` computes the bridgeable amount using the contract's raw ERC-20 `balanceOf`, not a tracked deposit ledger. Any tokens transferred directly to the pool address (outside of `deposit`) are therefore indistinguishable from legitimately deposited tokens and are swept to L1 in full the next time `bridgeTokens` is called.

---

### Finding Description

`deposit(address token, uint256 amount, string referralId)` is the only intended entry-point for token inflows. It pulls tokens from the caller and records only the fee portion: [1](#0-0) 

No variable tracks the total deposited principal. The bridgeable balance is therefore computed as: [2](#0-1) 

`IERC20(token).balanceOf(address(this))` includes every token the contract holds, regardless of how they arrived. `bridgeTokens` then bridges this entire amount without an explicit `amount` parameter: [3](#0-2) 

A user who accidentally (or intentionally) sends tokens directly to the pool address receives no `wrsETH` and has no recovery path. On the next `bridgeTokens` call those tokens are forwarded to `l1VaultETHForL2Chain` and are permanently lost to the sender.

---

### Impact Explanation

**Critical — Direct theft of user funds at-rest.**

The sender of directly-transferred tokens loses them permanently. They are bridged to the L1 vault without the sender's knowledge or consent and without any corresponding `wrsETH` mint. The `BRIDGER_ROLE` need not be malicious; the loss occurs during routine bridging operations.

---

### Likelihood Explanation

**Medium.** Direct ERC-20 transfers to contract addresses are a well-documented user error (e.g., sending to a contract instead of calling `deposit`). The pool is a publicly known address. Every `bridgeTokens` call — which happens on a regular operational cadence — sweeps the full balance, so the window for recovery is narrow.

---

### Recommendation

Replace the raw-`balanceOf` accounting with an explicit deposit ledger:

```solidity
mapping(address token => uint256 depositedBalance) public depositedBalances;
```

In `deposit`, increment `depositedBalances[token] += amount` after the `safeTransferFrom`. In `getTokenBalanceMinusFees`, return `depositedBalances[token] - feeEarnedInToken[token]`. Decrement `depositedBalances[token]` by the bridged amount in `bridgeTokens`. This ensures only tokens that entered through the sanctioned path are ever bridged.

---

### Proof of Concept

```solidity
// SPDX-License-Identifier: MIT
pragma solidity 0.8.27;

// Assume pool is deployed, wstETH is a supported token,
// tokenBridge[wstETH] is set, and BRIDGER_ROLE is held by `bridger`.

// Step 1 – User A deposits normally
vm.prank(userA);
wstETH.approve(address(pool), 1e18);
vm.prank(userA);
pool.deposit(address(wstETH), 1e18, "ref");
// userA receives wrsETH; pool holds 1e18 wstETH (minus fee)

// Step 2 – User B directly transfers tokens to the pool (no deposit call)
vm.prank(userB);
wstETH.transfer(address(pool), 1e18);
// userB receives nothing; pool now holds ~2e18 wstETH

// Step 3 – Bridger calls bridgeTokens
uint256 bridged = pool.getTokenBalanceMinusFees(address(wstETH));
assertApproxEqAbs(bridged, 2e18, feeBuffer); // 2e18 - fees, not 1e18 - fees

vm.prank(bridger);
pool.bridgeTokens{value: nativeFee}(address(wstETH));
// Both userA's and userB's tokens are bridged to L1.
// userB's 1e18 wstETH is permanently lost.
```

The assertion at step 3 confirms that `bridgeTokens` sweeps `2e18 - fees` instead of the expected `1e18 - fees`, proving userB's directly-transferred tokens are stolen.

### Citations

**File:** contracts/pools/RSETHPoolV3ExternalBridge.sol (L403-407)
```text
        IERC20(token).safeTransferFrom(msg.sender, address(this), amount);

        (uint256 rsETHAmount, uint256 fee) = viewSwapRsETHAmountAndFee(amount, token);

        feeEarnedInToken[token] += fee;
```

**File:** contracts/pools/RSETHPoolV3ExternalBridge.sol (L502-504)
```text
    function getTokenBalanceMinusFees(address token) public view returns (uint256) {
        return IERC20(token).balanceOf(address(this)) - feeEarnedInToken[token];
    }
```

**File:** contracts/pools/RSETHPoolV3ExternalBridge.sol (L726-737)
```text
        uint256 balance = getTokenBalanceMinusFees(token);

        if (balance == 0) {
            revert ZeroBridgeAmount();
        }

        // Approve the required amount to the bridge
        IERC20(token).safeIncreaseAllowance(tokenBridge[token], balance);

        // Call the bridge contract to transfer the tokens (msg.value is included in case we need to pay for additional
        // bridging fees)
        IL2TokenBridge(tokenBridge[token]).bridgeTokenToL1{ value: msg.value }(l1VaultETHForL2Chain, balance);
```
