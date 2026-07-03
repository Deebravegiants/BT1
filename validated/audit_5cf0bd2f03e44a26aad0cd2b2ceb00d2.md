Audit Report

## Title
Uninitialized `tokenFeeBps` for Newly Added Tokens Allows Fee-Free Deposits - (File: `contracts/pools/RSETHPool.sol`)

## Summary
`addSupportedToken` never initializes `tokenFeeBps[token]`, leaving it at the Solidity default of `0`. Any depositor can call `deposit` between `addSupportedToken` and a subsequent `setTokenFeeBps` call and receive rsETH with zero protocol fee deducted. The fee loss is permanent and unrecoverable for every deposit settled during this window.

## Finding Description
`addSupportedToken` (L637–656) sets `supportedTokenOracle[token]` and `tokenBridge[token]` but never writes `tokenFeeBps[token]`:

```solidity
// L651-653
supportedTokenList.push(token);
supportedTokenOracle[token] = oracle;
tokenBridge[token] = bridge;
// tokenFeeBps[token] remains 0
```

`viewSwapRsETHAmountAndFee(uint256, address)` (L335–336) reads this uninitialized value directly:

```solidity
uint256 feeBpsForToken = tokenFeeBps[token]; // == 0
fee = amount * feeBpsForToken / 10_000;       // == 0
```

`deposit` (L298–300) uses the result without any floor check:

```solidity
(uint256 rsETHAmount, uint256 fee) = viewSwapRsETHAmountAndFee(amount, token);
feeEarnedInToken[token] += fee; // += 0
IERC20(address(wrsETH)).safeTransfer(msg.sender, rsETHAmount);
```

`setTokenFeeBps` (L583–594) is a separate, independent admin call under `DEFAULT_ADMIN_ROLE`, while `addSupportedToken` is under `TIMELOCK_ROLE`. Because these are distinct roles, they cannot be batched into a single atomic transaction without an external multicall, making the zero-fee window structurally unavoidable on every new token addition. No existing guard in `deposit` or `viewSwapRsETHAmountAndFee` checks for a zero fee or a minimum `feeBps` value.

## Impact Explanation
**High — Theft of unclaimed yield.** Protocol fee revenue is permanently lost for all deposits settled before `setTokenFeeBps` is confirmed. The `feeEarnedInToken` accumulator records `0` for these deposits; there is no retroactive correction mechanism. A single large deposit during the window can deprive the protocol of a material amount of fee revenue (e.g., a 1,000-token deposit at an intended 50 bps fee loses 5 tokens worth of fees permanently).

## Likelihood Explanation
**Medium.** Adding a new supported token is a routine protocol operation. The two-step pattern is structurally required by the current role separation (`TIMELOCK_ROLE` vs `DEFAULT_ADMIN_ROLE`). Any depositor monitoring on-chain `AddSupportedToken` events can immediately call `deposit` before `setTokenFeeBps` is confirmed. No special capability beyond a standard EOA and token balance is required. The window spans at least one block and potentially many blocks depending on admin response time.

## Recommendation
Add a `feeBps` parameter to `addSupportedToken` and initialize `tokenFeeBps[token]` atomically in the same call:

```solidity
function addSupportedToken(
    address token,
    address oracle,
    address bridge,
    uint256 feeBps
) external onlyRole(TIMELOCK_ROLE) {
    // ... existing checks ...
    if (feeBps > 10_000) revert InvalidFeeAmount();
    supportedTokenList.push(token);
    supportedTokenOracle[token] = oracle;
    tokenBridge[token] = bridge;
    tokenFeeBps[token] = feeBps; // atomic initialization
    emit AddSupportedToken(token, oracle, bridge);
}
```

## Proof of Concept
1. `TIMELOCK_ROLE` calls `addSupportedToken(wstETH, oracle, bridge)` — `tokenFeeBps[wstETH]` is `0`.
2. Attacker observes the `AddSupportedToken` event and calls `deposit(wstETH, 1_000e18, "")`.
3. `viewSwapRsETHAmountAndFee(1_000e18, wstETH)` computes `fee = 1_000e18 * 0 / 10_000 = 0`; attacker receives full rsETH equivalent with no fee.
4. `feeEarnedInToken[wstETH] += 0` — loss is recorded as zero and is unrecoverable.
5. `DEFAULT_ADMIN_ROLE` later calls `setTokenFeeBps(wstETH, 50)`, but the attacker's deposit has already settled at 0%.

**Foundry test sketch:**
```solidity
function test_zeroFeeWindowOnAddToken() public {
    vm.prank(timelockRole);
    pool.addSupportedToken(address(wstETH), oracle, bridge);
    // tokenFeeBps[wstETH] == 0 at this point
    vm.prank(attacker);
    pool.deposit(address(wstETH), 1_000e18, "");
    assertEq(pool.feeEarnedInToken(address(wstETH)), 0);
    // Admin sets fee after the fact
    vm.prank(adminRole);
    pool.setTokenFeeBps(address(wstETH), 50);
    // feeEarnedInToken still 0 — loss is permanent
    assertEq(pool.feeEarnedInToken(address(wstETH)), 0);
}
```