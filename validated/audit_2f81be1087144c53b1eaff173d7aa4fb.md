The code confirms the claim exactly. `addSupportedToken` never initializes `tokenFeeBps[token]`, `deposit` reads it directly with no guard, and `setTokenFeeBps` is a separate admin call. The zero-fee window is real and exploitable by any unprivileged depositor.

Audit Report

## Title
Missing Default Fee Initialization in `addSupportedToken` Enables Fee-Free Deposits - (File: contracts/pools/RSETHPool.sol)

## Summary
`RSETHPool.addSupportedToken` registers a new ERC-20 token but never initializes `tokenFeeBps[token]`, leaving it at the Solidity default of `0`. Any depositor can immediately call `deposit(token, amount, referralId)` and receive rsETH at the full oracle rate with zero fee deducted. The zero-fee window persists until a separate `DEFAULT_ADMIN_ROLE` call to `setTokenFeeBps` is made, during which the protocol collects no swap-fee revenue on that token.

## Finding Description
`addSupportedToken` (lines 637–655) sets `supportedTokenOracle[token]`, `tokenBridge[token]`, and appends to `supportedTokenList`, but never writes to `tokenFeeBps[token]`: [1](#0-0) 

`tokenFeeBps[token]` therefore silently defaults to `0`. The public `deposit` function (lines 284–305) immediately delegates to `viewSwapRsETHAmountAndFee(amount, token)`: [2](#0-1) 

`viewSwapRsETHAmountAndFee` (lines 326–347) reads `tokenFeeBps[token]` directly with no guard checking whether a fee has been explicitly configured: [3](#0-2) 

With `feeBpsForToken = 0`, `fee = 0` and `amountAfterFee = amount`, so the depositor receives the full oracle-rate rsETH conversion. `feeEarnedInToken[token]` remains `0` for every deposit made before `setTokenFeeBps` is called: [4](#0-3) 

The `onlySupportedToken` modifier only verifies the token is registered; it does not verify that a fee has been configured. There is no atomicity between `addSupportedToken` and `setTokenFeeBps` — they are separate role-gated calls (`TIMELOCK_ROLE` vs. `DEFAULT_ADMIN_ROLE`).

## Impact Explanation
**High — Theft of unclaimed yield.** The protocol is explicitly designed to collect swap fees on ERC-20 token deposits (evidenced by the `tokenFeeBps` mapping, `feeEarnedInToken` accounting, and `setTokenFeeBps` admin function). During the zero-fee window, depositors receive rsETH at the full oracle rate; `feeEarnedInToken[token]` accrues nothing; the BRIDGER_ROLE collects no fee revenue. The fee yield the protocol is designed to retain is instead captured by depositors, constituting theft of unclaimed yield.

## Likelihood Explanation
Low-to-Medium. The trigger condition arises on every `addSupportedToken` call. The `AddSupportedToken` event is publicly observable; any user monitoring on-chain events or the mempool can deposit immediately after token registration with no special privileges, no oracle manipulation, and no governance capture required. The window closes only when a separate `DEFAULT_ADMIN_ROLE` transaction executes `setTokenFeeBps`.

## Recommendation
Add a `_feeBps` parameter to `addSupportedToken` and set `tokenFeeBps[token] = _feeBps` atomically during registration, applying the same `_feeBps > 10_000 → revert InvalidFeeAmount()` guard already present in `setTokenFeeBps`. This eliminates the zero-fee window entirely:

```solidity
function addSupportedToken(address token, address oracle, address bridge, uint256 _feeBps)
    external onlyRole(TIMELOCK_ROLE)
{
    // ... existing checks ...
    if (_feeBps > 10_000) revert InvalidFeeAmount();
    supportedTokenList.push(token);
    supportedTokenOracle[token] = oracle;
    tokenBridge[token] = bridge;
    tokenFeeBps[token] = _feeBps;
    emit AddSupportedToken(token, oracle, bridge);
}
```

## Proof of Concept
1. Admin calls `addSupportedToken(tokenX, oracleX, bridgeX)` — `tokenFeeBps[tokenX]` is `0`.
2. Attacker observes the `AddSupportedToken` event and calls `deposit(tokenX, 1_000e18, "ref")` in the same or next block.
3. `viewSwapRsETHAmountAndFee(1_000e18, tokenX)` computes `feeBpsForToken = 0`, `fee = 0`, `amountAfterFee = 1_000e18`.
4. Attacker receives `rsETHAmount = 1_000e18 * tokenToETHRate / rsETHToETHrate` — full oracle-rate conversion, zero fee.
5. `feeEarnedInToken[tokenX]` remains `0`; protocol collects nothing.
6. Admin later calls `setTokenFeeBps(tokenX, 30)` — all prior deposits were fee-free.

**Foundry test sketch:**
```solidity
function test_zeroFeeWindowOnNewToken() public {
    vm.prank(timelockAdmin);
    pool.addSupportedToken(address(tokenX), address(oracleX), address(bridgeX));

    uint256 amount = 1_000e18;
    tokenX.mint(attacker, amount);
    vm.startPrank(attacker);
    tokenX.approve(address(pool), amount);
    pool.deposit(address(tokenX), amount, "ref");
    vm.stopPrank();

    assertEq(pool.feeEarnedInToken(address(tokenX)), 0); // fee never collected
}
```

### Citations

**File:** contracts/pools/RSETHPool.sol (L298-300)
```text
        (uint256 rsETHAmount, uint256 fee) = viewSwapRsETHAmountAndFee(amount, token);

        feeEarnedInToken[token] += fee;
```

**File:** contracts/pools/RSETHPool.sol (L335-337)
```text
        uint256 feeBpsForToken = tokenFeeBps[token];
        fee = amount * feeBpsForToken / 10_000;
        uint256 amountAfterFee = amount - fee;
```

**File:** contracts/pools/RSETHPool.sol (L583-593)
```text
    function setTokenFeeBps(
        address token,
        uint256 _feeBps
    )
        external
        onlyRole(DEFAULT_ADMIN_ROLE)
        onlySupportedToken(token)
    {
        if (_feeBps > 10_000) revert InvalidFeeAmount();
        tokenFeeBps[token] = _feeBps;
        emit TokenFeeBpsSet(token, _feeBps);
```

**File:** contracts/pools/RSETHPool.sol (L651-655)
```text
        supportedTokenList.push(token);
        supportedTokenOracle[token] = oracle;
        tokenBridge[token] = bridge;

        emit AddSupportedToken(token, oracle, bridge);
```
