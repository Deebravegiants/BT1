### Title
Arithmetic Underflow in `getTokenBalanceMinusFees` Permanently Freezes Token Collateral When a Rebasing Token Suffers a Negative Rebase — (`contracts/pools/RSETHPool.sol`)

---

### Summary

`getTokenBalanceMinusFees` performs an unchecked subtraction between the live ERC-20 balance and the stored `feeEarnedInToken` accumulator. If a supported rebasing token undergoes a negative rebase that reduces the pool's actual balance below the accumulated fee amount, every downstream call that reads this function reverts with an arithmetic underflow, permanently locking all token collateral (including the fee portion) with no recovery path.

---

### Finding Description

`getTokenBalanceMinusFees` is defined as:

```solidity
// contracts/pools/RSETHPool.sol, line 396-398
function getTokenBalanceMinusFees(address token) public view returns (uint256) {
    return IERC20(token).balanceOf(address(this)) - feeEarnedInToken[token];
}
``` [1](#0-0) 

Under Solidity 0.8, this subtraction reverts if `balanceOf(pool) < feeEarnedInToken[token]`. The function is called unconditionally in two critical paths:

**`bridgeTokens`** (line 556):
```solidity
uint256 balance = getTokenBalanceMinusFees(token);
if (balance == 0) { revert ZeroBridgeAmount(); }
``` [2](#0-1) 

**`moveAssetsForBridging(address, uint256)`** (line 472):
```solidity
uint256 tokenBalanceMinusFees = getTokenBalanceMinusFees(token);
if (amount > tokenBalanceMinusFees) revert InsufficientBalanceInPool();
``` [3](#0-2) 

`feeEarnedInToken[token]` is incremented on every token deposit: [4](#0-3) 

There is no admin function to zero out or adjust `feeEarnedInToken[token]` independently of `withdrawFees`. `withdrawFees(receiver, token)` itself attempts `safeTransfer(receiver, feeEarnedInToken[token])`, which also fails if the pool's balance is below that amount — so even the fee-withdrawal escape hatch is broken. [5](#0-4) 

---

### Impact Explanation

Once the underflow condition is triggered:

- `bridgeTokens` is permanently uncallable for that token.
- `moveAssetsForBridging` is permanently uncallable for that token.
- `withdrawFees` for that token also fails (insufficient balance for the transfer).
- There is no emergency-drain or `feeEarnedInToken` reset function anywhere in the contract.

All token collateral held by the pool — both the user principal portion and the fee portion — is permanently frozen with no on-chain recovery path. This matches the **Critical — Permanent freezing of funds** impact category.

---

### Likelihood Explanation

The precondition is that a rebasing token (e.g., stETH) is added via `addSupportedToken` (requires `TIMELOCK_ROLE`) and that deposits accumulate a non-zero `feeEarnedInToken`. A negative rebase — a known, documented property of rebasing tokens — then reduces the pool balance below the fee accumulator. This is not an admin compromise; it is a legitimate configuration choice combined with a predictable external token event. The current production deployment uses wstETH (non-rebasing), so the risk is latent but real if the token list is ever expanded.

---

### Recommendation

Replace the bare subtraction with a saturating or guarded version:

```solidity
function getTokenBalanceMinusFees(address token) public view returns (uint256) {
    uint256 bal = IERC20(token).balanceOf(address(this));
    uint256 fee = feeEarnedInToken[token];
    return bal > fee ? bal - fee : 0;
}
```

Additionally, add an admin function to correct `feeEarnedInToken[token]` in emergency situations, and document that rebasing tokens are not supported unless this accounting is redesigned.

---

### Proof of Concept

```solidity
// Local fork / unit test — no mainnet interaction
function testRebaseDownFreezesPool() public {
    // 1. Deploy MockRebasingToken with initial supply 1000e18
    MockRebasingToken token = new MockRebasingToken(1000e18);
    MockOracle oracle = new MockOracle(1e18);
    MockBridge bridge = new MockBridge();

    // 2. Admin adds token as supported (TIMELOCK_ROLE action)
    pool.addSupportedToken(address(token), address(oracle), address(bridge));
    pool.setTokenFeeBps(address(token), 100); // 1% fee

    // 3. User deposits 100e18 tokens → feeEarnedInToken[token] = 1e18
    token.approve(address(pool), 100e18);
    pool.deposit(address(token), 100e18, "ref");
    // pool balance = 100e18, feeEarnedInToken = 1e18

    // 4. Negative rebase: pool balance drops to 0.5e18 (below fee of 1e18)
    token.rebase(address(pool), 0.5e18); // sets balanceOf(pool) = 0.5e18

    // 5. bridgeTokens now reverts with arithmetic underflow
    vm.expectRevert(); // Panic: arithmetic underflow
    pool.bridgeTokens(address(token));

    // 6. moveAssetsForBridging also reverts
    vm.expectRevert();
    pool.moveAssetsForBridging(address(token), 1);

    // 7. withdrawFees also reverts (safeTransfer of 1e18 from a 0.5e18 balance)
    vm.expectRevert();
    pool.withdrawFees(address(this), address(token));
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

**File:** contracts/pools/RSETHPool.sol (L556-559)
```text
        uint256 balance = getTokenBalanceMinusFees(token);

        if (balance == 0) {
            revert ZeroBridgeAmount();
```
