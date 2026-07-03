Audit Report

## Title
Precision Loss in `viewSwapRsETHAmountAndFee()` Allows Token Deposit to Return Zero rsETH Output - (File: contracts/pools/RSETHPool.sol, contracts/pools/RSETHPoolV3.sol, contracts/pools/RSETHPoolV3ExternalBridge.sol, contracts/pools/RSETHPoolV3WithNativeChainBridge.sol, contracts/pools/RSETHPoolNoWrapper.sol)

## Summary
All five L2 pool contracts compute `rsETHAmount = amountAfterFee * tokenToETHRate / rsETHToETHrate` using integer division with no zero-output guard. When a user deposits a sufficiently small token amount such that `amountAfterFee * tokenToETHRate < rsETHToETHrate`, the division truncates to zero. The deposit function unconditionally proceeds: it takes the user's tokens via `safeTransferFrom` and then transfers or mints zero rsETH/wrsETH in return, permanently retaining the deposited tokens in the pool with no corresponding output.

## Finding Description
The root cause is integer division truncation in `viewSwapRsETHAmountAndFee(uint256 amount, address token)` across all five pool contracts:

- `RSETHPool.sol` L346: `rsETHAmount = amountAfterFee * tokenToETHRate / rsETHToETHrate`
- `RSETHPoolV3.sol` L334: same formula
- `RSETHPoolV3ExternalBridge.sol` L452: same formula
- `RSETHPoolV3WithNativeChainBridge.sol` L370: same formula
- `RSETHPoolNoWrapper.sol` L311: same formula

In each deposit path, the only input guard is `if (amount == 0) revert InvalidAmount()`, which validates the input but not the computed output. After `safeTransferFrom` moves the user's tokens to the pool, the zero `rsETHAmount` is used unconditionally:

- `RSETHPool.sol` L302: `IERC20(address(wrsETH)).safeTransfer(msg.sender, rsETHAmount)` — `safeTransfer(..., 0)` is a no-op under standard ERC-20 semantics, succeeds silently
- `RSETHPoolV3.sol` L290: `wrsETH.mint(msg.sender, rsETHAmount)` — mints zero
- `RSETHPoolNoWrapper.sol` L268: `rsETH.safeTransfer(msg.sender, rsETHAmount)` — transfers zero

Concrete trigger: with `tokenToETHRate = 1e18` (stETH ≈ 1 ETH) and `rsETHToETHrate = 1.05e18`, depositing `amount = 1` wei (with `feeBps = 0`) yields `rsETHAmount = 1 * 1e18 / 1.05e18 = 0`. The 1 wei of stETH is absorbed by the pool; the user receives nothing. The absorbed amount is not credited to `feeEarnedInToken` either — it silently inflates the pool's general token balance.

## Impact Explanation
**Low — Contract fails to deliver promised returns.** The deposit function's core invariant — that a non-zero token deposit yields a non-zero rsETH output — is violated. The user's deposited tokens are permanently retained by the pool with no corresponding rsETH minted or transferred. The per-transaction loss is sub-wei to a few wei of an LST, making the absolute monetary loss negligible. However, the contract silently accepts a deposit and delivers nothing, which is a clear failure to deliver promised returns.

## Likelihood Explanation
**Low.** The truncation condition requires `amountAfterFee * tokenToETHRate < rsETHToETHrate`. With current rates near `1e18` for both stETH and rsETH, the threshold is approximately 1–2 wei of the deposited token. Normal users depositing meaningful amounts are entirely unaffected. The threshold rises if rsETH appreciates significantly relative to a supported token, but remains in the sub-wei range under realistic market conditions. Any unprivileged user can trigger this by calling `deposit(token, 1, "")` with a supported token.

## Recommendation
Add an explicit zero-output guard immediately after computing `rsETHAmount` in every pool's token deposit path:

```solidity
(uint256 rsETHAmount, uint256 fee) = viewSwapRsETHAmountAndFee(amount, token);
if (rsETHAmount == 0) revert InvalidAmount();
```

This should be applied to `RSETHPool.sol` (after L298), `RSETHPoolV3.sol` (after L286), `RSETHPoolV3ExternalBridge.sol` (in its token deposit path), `RSETHPoolV3WithNativeChainBridge.sol` (in its token deposit path), and `RSETHPoolNoWrapper.sol` (after L264). The same guard should also be applied to the ETH deposit paths where `rsETHAmount = amountAfterFee * 1e18 / rsETHToETHrate` can similarly truncate to zero for sub-wei ETH deposits.

## Proof of Concept
1. Deploy or fork any of the five pool contracts with a supported LST token (e.g., stETH).
2. Set or observe: `rsETHToETHrate = 1.05e18`, `tokenToETHRate = 1e18`, `feeBps = 0`.
3. Approve 1 wei of the LST token to the pool contract.
4. Call `deposit(token, 1, "")`.
5. Observe: `safeTransferFrom` moves 1 wei of LST from caller to pool (caller balance decreases by 1).
6. `viewSwapRsETHAmountAndFee` returns `rsETHAmount = 0`, `fee = 0`.
7. `safeTransfer(msg.sender, 0)` (or `mint(msg.sender, 0)`) executes successfully, transferring/minting nothing.
8. Caller's 1 wei of LST is permanently in the pool; `feeEarnedInToken[token]` is unchanged (0 fee credited); pool's token balance increased by 1 with no accounting entry.

Foundry fuzz test plan: fuzz `amount` over `[1, rsETHToETHrate / tokenToETHRate]` and assert that `deposit` reverts when `viewSwapRsETHAmountAndFee` would return `rsETHAmount == 0`, confirming the missing guard.