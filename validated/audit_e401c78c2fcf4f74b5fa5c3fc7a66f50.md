Audit Report

## Title
Uninitialized `tokenFeeBps` Mapping Allows Zero-Fee Token Deposits After `addSupportedToken()` - (File: contracts/pools/RSETHPool.sol)

## Summary
`RSETHPool.sol` never initializes `tokenFeeBps[token]` when a new token is added via `addSupportedToken()`, leaving it at the Solidity default of zero. Any depositor who calls `deposit(token, amount, referralId)` in the window between `addSupportedToken()` and a subsequent `setTokenFeeBps()` call pays zero protocol fee and receives the full token value converted to rsETH, permanently depriving the protocol of that fee revenue.

## Finding Description
`tokenFeeBps` is declared at line 88:
```solidity
mapping(address token => uint256 feeBps) public tokenFeeBps;
```
`addSupportedToken()` (lines 637–656) sets `supportedTokenOracle[token]` and `tokenBridge[token]` but never touches `tokenFeeBps[token]`, leaving it at 0. The fee setter is a completely separate privileged call under `DEFAULT_ADMIN_ROLE` (lines 583–594), while `addSupportedToken` requires `TIMELOCK_ROLE`, making atomic initialization structurally impossible in a single transaction.

`viewSwapRsETHAmountAndFee(amount, token)` (lines 335–336) reads the mapping directly:
```solidity
uint256 feeBpsForToken = tokenFeeBps[token];
fee = amount * feeBpsForToken / 10_000;
```
With `feeBpsForToken == 0`, `fee == 0` and `amountAfterFee == amount`. The `deposit()` function (lines 298–300) then credits `feeEarnedInToken[token] += 0`, so the protocol accumulates nothing. No guard in `deposit()` or `viewSwapRsETHAmountAndFee()` checks whether `tokenFeeBps[token]` has been explicitly set.

## Impact Explanation
Every deposit made between `addSupportedToken()` and `setTokenFeeBps()` pays zero fee. The protocol's `feeEarnedInToken[token]` accumulates nothing for those deposits, permanently losing that fee revenue. This constitutes **theft of unclaimed yield** (High): the depositor receives more rsETH than the intended post-fee amount, and the protocol's fee accumulator is permanently short by the fee that should have been collected.

## Likelihood Explanation
The window is structurally guaranteed every time a new token is listed: `addSupportedToken()` (TIMELOCK_ROLE) and `setTokenFeeBps()` (DEFAULT_ADMIN_ROLE) are separate transactions by potentially separate roles. An attacker monitoring the mempool can front-run or immediately follow the `addSupportedToken()` transaction with a large `deposit()` call before `setTokenFeeBps()` is confirmed. Even without front-running, any deposit in the gap—which may span multiple blocks or longer if the admin delays—is affected. The exploit requires no special privileges; `deposit()` is a public function callable by any address.

## Recommendation
Initialize `tokenFeeBps[token]` inside `addSupportedToken()` by accepting a `_feeBps` parameter:
```diff
function addSupportedToken(
    address token,
    address oracle,
-   address bridge
+   address bridge,
+   uint256 _feeBps
) external onlyRole(TIMELOCK_ROLE) {
    // ...
+   if (_feeBps > 10_000) revert InvalidFeeAmount();
    supportedTokenList.push(token);
    supportedTokenOracle[token] = oracle;
    tokenBridge[token] = bridge;
+   tokenFeeBps[token] = _feeBps;
+   emit TokenFeeBpsSet(token, _feeBps);
    emit AddSupportedToken(token, oracle, bridge);
}
```
This eliminates the uninitialized window entirely, mirroring how `feeBps` is set atomically in `initialize()` for ETH deposits.

## Proof of Concept
**Call sequence (no privileged attacker required):**

1. Admin calls `addSupportedToken(rETH, rETHOracle, rETHBridge)` — `tokenFeeBps[rETH]` is now 0 (Solidity default).
2. Attacker calls `deposit(rETH, 100e18, "")` before `setTokenFeeBps` is confirmed.
3. Inside `viewSwapRsETHAmountAndFee(100e18, rETH)`:
   - `feeBpsForToken = 0`
   - `fee = 100e18 * 0 / 10_000 = 0`
   - `amountAfterFee = 100e18`
   - `rsETHAmount = 100e18 * tokenToETHRate / rsETHToETHrate` (full value, no fee)
4. `feeEarnedInToken[rETH] += 0` — protocol earns nothing.
5. Admin later calls `setTokenFeeBps(rETH, 50)` — too late; the deposit already settled at 0%.

**Foundry test plan:** Deploy `RSETHPool` with a mock oracle returning a non-zero rate. Call `addSupportedToken`. Without calling `setTokenFeeBps`, call `deposit(token, amount, "")`. Assert `feeEarnedInToken[token] == 0` and that the rsETH transferred equals `amount * tokenToETHRate / rsETHToETHrate` (i.e., no fee deducted). Then call `setTokenFeeBps(token, 50)` and repeat the deposit; assert `feeEarnedInToken[token] > 0`. The contrast proves the vulnerability.