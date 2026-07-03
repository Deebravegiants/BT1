### Title
Arithmetic Underflow in `getTokenBalanceMinusFees` Permanently Freezes All Token Collateral After Negative Rebase — (`contracts/pools/RSETHPool.sol`)

---

### Summary

`getTokenBalanceMinusFees` performs an unchecked subtraction of `feeEarnedInToken[token]` from `IERC20(token).balanceOf(address(this))`. If a supported token is a rebasing token and undergoes a negative rebase that reduces the pool's balance below the accrued fee, every downstream call that invokes this function reverts with an arithmetic underflow, permanently freezing all token collateral held in the pool — including the fee portion itself.

---

### Finding Description

`getTokenBalanceMinusFees` is implemented identically across all pool variants:

```solidity
function getTokenBalanceMinusFees(address token) public view returns (uint256) {
    return IERC20(token).balanceOf(address(this)) - feeEarnedInToken[token];
}
``` [1](#0-0) 

In Solidity 0.8, this subtraction reverts on underflow. `feeEarnedInToken[token]` is a monotonically increasing counter that is only decremented when `withdrawFees` is called:

```solidity
feeEarnedInToken[token] += fee;
``` [2](#0-1) 

If the token's `balanceOf(pool)` is reduced externally (e.g., by a negative rebase) to a value strictly less than `feeEarnedInToken[token]`, the subtraction underflows and every function that calls `getTokenBalanceMinusFees` reverts:

**`bridgeTokens`** — calls `getTokenBalanceMinusFees` unconditionally: [3](#0-2) 

**`moveAssetsForBridging(address, uint256)`** — calls `getTokenBalanceMinusFees` unconditionally: [4](#0-3) 

**`withdrawFees(address, address)`** — attempts `safeTransfer(receiver, feeEarnedInToken[token])`, which also fails because the pool no longer holds enough balance: [5](#0-4) 

**`removeSupportedToken`** — requires `balanceOf(pool) == 0` before removal, so it cannot be used to clean up the token while any balance remains: [6](#0-5) 

The same pattern is present in all pool variants: [7](#0-6) [8](#0-7) [9](#0-8) 

---

### Impact Explanation

Once `balanceOf(pool) < feeEarnedInToken[token]`:

- `bridgeTokens` permanently reverts — tokens cannot be bridged to L1.
- `moveAssetsForBridging` permanently reverts — tokens cannot be manually moved.
- `withdrawFees` permanently reverts — the fee portion cannot be recovered.
- `removeSupportedToken` permanently reverts (balance ≠ 0) — the token cannot be delisted.

The only recovery path is an external donation of tokens to the pool to bring `balanceOf` back above `feeEarnedInToken[token]`. This is not guaranteed and cannot be enforced by the protocol. All token collateral — both the principal and the fee — is permanently frozen.

---

### Likelihood Explanation

The precondition requires:
1. A rebasing token is added via `addSupportedToken` (a legitimate `TIMELOCK_ROLE` action — not an admin compromise).
2. Deposits accumulate `feeEarnedInToken[token] > 0`.
3. A negative rebase reduces `balanceOf(pool)` below `feeEarnedInToken[token]`.

The `addSupportedToken` function has no guard against rebasing tokens: [10](#0-9) 

The current production token (wstETH) is non-rebasing, so this is not currently triggered. However, the contract is generic and the code contains no documentation or enforcement preventing rebasing tokens from being added. If the protocol ever expands to support a rebasing token (e.g., stETH directly), this vulnerability activates automatically upon any negative rebase event.

---

### Recommendation

Replace the bare subtraction with a safe check:

```solidity
function getTokenBalanceMinusFees(address token) public view returns (uint256) {
    uint256 bal = IERC20(token).balanceOf(address(this));
    uint256 fee = feeEarnedInToken[token];
    return bal >= fee ? bal - fee : 0;
}
```

Additionally, document that rebasing tokens are explicitly unsupported, or add a guard in `addSupportedToken` to reject tokens whose balance can decrease externally.

---

### Proof of Concept

```solidity
// Local fork or unit test — no mainnet required
function testRebaseDownFreezesPool() public {
    // 1. Deploy MockRebasingToken (balance decreases on rebase)
    MockRebasingToken token = new MockRebasingToken();
    MockOracle oracle = new MockOracle(1e18);
    MockBridge bridge = new MockBridge();

    // 2. Add as supported token (TIMELOCK_ROLE action)
    vm.prank(timelockAdmin);
    pool.addSupportedToken(address(token), address(oracle), address(bridge));

    // 3. User deposits 100 tokens; fee = 1 token (1% feeBps)
    token.mint(user, 100e18);
    vm.prank(user);
    token.approve(address(pool), 100e18);
    vm.prank(user);
    pool.deposit(address(token), 100e18, "ref");
    // pool.feeEarnedInToken[token] == 1e18
    // pool.balanceOf(token) == 100e18

    // 4. Trigger negative rebase: pool balance drops to 0.5e18 (below fee)
    token.rebase(address(pool), 0.5e18); // sets balanceOf(pool) = 0.5e18

    // 5. Assert bridgeTokens reverts with arithmetic underflow
    vm.prank(bridger);
    vm.expectRevert(); // arithmetic underflow in getTokenBalanceMinusFees
    pool.bridgeTokens(address(token));

    // 6. Assert moveAssetsForBridging also reverts
    vm.prank(bridger);
    vm.expectRevert();
    pool.moveAssetsForBridging(address(token), 0.1e18);

    // 7. Assert withdrawFees also reverts (safeTransfer of 1e18 when balance is 0.5e18)
    vm.prank(bridger);
    vm.expectRevert();
    pool.withdrawFees(receiver, address(token));
    // All 0.5e18 tokens are permanently frozen.
}
```

### Citations

**File:** contracts/pools/RSETHPool.sol (L300-300)
```text
        feeEarnedInToken[token] += fee;
```

**File:** contracts/pools/RSETHPool.sol (L396-398)
```text
    function getTokenBalanceMinusFees(address token) public view returns (uint256) {
        return IERC20(token).balanceOf(address(this)) - feeEarnedInToken[token];
    }
```

**File:** contracts/pools/RSETHPool.sol (L438-440)
```text
        uint256 amountToSendInToken = feeEarnedInToken[token];
        feeEarnedInToken[token] = 0;
        IERC20(token).safeTransfer(receiver, amountToSendInToken);
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

**File:** contracts/pools/RSETHPool.sol (L637-655)
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
```

**File:** contracts/pools/RSETHPool.sol (L662-663)
```text
        if (supportedTokenList[tokenIndex] != token) revert TokenNotFoundError();
        if (IERC20(token).balanceOf(address(this)) != 0) revert TokenBalanceNotZero();
```

**File:** contracts/pools/RSETHPoolV3WithNativeChainBridge.sol (L384-386)
```text
    function getTokenBalanceMinusFees(address token) public view returns (uint256) {
        return IERC20(token).balanceOf(address(this)) - feeEarnedInToken[token];
    }
```

**File:** contracts/pools/RSETHPoolV3ExternalBridge.sol (L502-504)
```text
    function getTokenBalanceMinusFees(address token) public view returns (uint256) {
        return IERC20(token).balanceOf(address(this)) - feeEarnedInToken[token];
    }
```

**File:** contracts/pools/RSETHPoolNoWrapper.sol (L361-363)
```text
    function getTokenBalanceMinusFees(address token) public view returns (uint256) {
        return IERC20(token).balanceOf(address(this)) - feeEarnedInToken[token];
    }
```
