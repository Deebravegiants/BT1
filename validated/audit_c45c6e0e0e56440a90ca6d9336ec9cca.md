Audit Report

## Title
Zero wrsETH Minted on Dust Deposits Due to Integer Division Truncation — (File: contracts/pools/RSETHPoolV3.sol)

## Summary
Every L2 pool deposit function computes `rsETHAmount` via integer division that silently truncates to zero for dust-sized inputs. When this occurs, the deposit is accepted, the user's ETH or ERC-20 tokens are retained by the contract, and zero wrsETH is minted or transferred to the user. The deposited assets are subsequently bridged to L1 as part of the collective pool balance, permanently unrecoverable by the depositor.

## Finding Description
In `RSETHPoolV3.sol`, `viewSwapRsETHAmountAndFee` computes the output amount as:

```solidity
rsETHAmount = amountAfterFee * 1e18 / rsETHToETHrate;   // ETH path
rsETHAmount = amountAfterFee * tokenToETHRate / rsETHToETHrate; // token path
```

When `amountAfterFee * 1e18 < rsETHToETHrate` (ETH path) or `amountAfterFee * tokenToETHRate < rsETHToETHrate` (token path), Solidity integer division produces `rsETHAmount = 0`. The deposit functions contain only an input-side guard:

```solidity
if (amount == 0) revert InvalidAmount();
```

This guard does not protect against a non-zero input producing a zero output. After `viewSwapRsETHAmountAndFee` returns `(0, fee)`, execution continues unconditionally:

- ETH path: `wrsETH.mint(msg.sender, 0)` — mints nothing, no revert.
- Token path: `IERC20(token).safeTransferFrom(msg.sender, address(this), amount)` executes first (tokens leave the user), then `wrsETH.mint(msg.sender, 0)` — user loses tokens, receives nothing.

The same pattern is confirmed across all pool variants:
- `RSETHPoolV3.sol` lines 256–262 (ETH), 282–290 (token) / computation lines 307, 334
- `RSETHPoolV2.sol` lines 210–216 / computation line 233
- `RSETHPool.sol` lines 269–275 (ETH), 294–302 (token) / computation lines 319, 346
- `RSETHPoolNoWrapper.sol` lines 277–285 (ETH), 292–311 (token)
- `RSETHPoolV3ExternalBridge.sol` lines 375–381 (ETH), 401–409 (token) / computation lines 426, 452
- `RSETHPoolV3WithNativeChainBridge.sol` lines 292–298 (ETH), 318–326 (token) / computation lines 343, 370

## Impact Explanation
The depositor's ETH or ERC-20 tokens are permanently inaccessible to them: the assets are pooled with the contract's collective balance and bridged to L1, but the user holds no wrsETH and therefore has no claim. This constitutes permanent freezing of the deposited funds from the user's perspective, matching **Critical — Permanent freezing of funds** from the allowed impact scope. The claim self-classifies as Low, but the user unambiguously loses their deposited assets with no recovery path, which is a stronger impact than "fails to deliver promised returns, but doesn't lose value."

## Likelihood Explanation
Low. For the ETH path, the condition triggers when `amountAfterFee ≤ 1 wei` (with `rsETHToETHrate ≈ 1.05e18`, `1 * 1e18 / 1.05e18 = 0`). For the token path, the threshold depends on `tokenToETHRate / rsETHToETHrate` but remains in the single-digit wei range for pegged assets. Accidental triggering by a normal user is extremely unlikely; deliberate triggering requires sending dust amounts. The per-call loss is negligible in absolute terms but the loss is permanent and unrecoverable.

## Recommendation
Add a zero-output guard immediately after `viewSwapRsETHAmountAndFee` in every deposit function across all pool variants:

```solidity
(uint256 rsETHAmount, uint256 fee) = viewSwapRsETHAmountAndFee(amount);
if (rsETHAmount == 0) revert InvalidAmount();
feeEarnedInETH += fee;
wrsETH.mint(msg.sender, rsETHAmount);
```

For the token deposit overload, the guard must be placed **before** `safeTransferFrom` to prevent token loss:

```solidity
(uint256 rsETHAmount, uint256 fee) = viewSwapRsETHAmountAndFee(amount, token);
if (rsETHAmount == 0) revert InvalidAmount();
IERC20(token).safeTransferFrom(msg.sender, address(this), amount);
```

Apply identically to all six pool variants listed above.

## Proof of Concept
1. Deploy `RSETHPoolV3` with `rsETHOracle` returning `rsETHToETHrate = 1.05e18` and `feeBps = 0`.
2. Call `deposit("")` with `msg.value = 1 wei`.
3. `fee = 1 * 0 / 10_000 = 0`; `amountAfterFee = 1`.
4. `rsETHAmount = 1 * 1e18 / 1.05e18 = 0` (integer truncation).
5. `wrsETH.mint(msg.sender, 0)` executes without revert.
6. Caller's balance: 1 wei ETH deducted, 0 wrsETH received.
7. The 1 wei ETH remains in the pool, is later bridged to L1 via `moveAssetsToL1`, and the caller has no token to reclaim it.

Foundry fuzz test to confirm: fuzz `amount` in `[1, rsETHToETHrate / 1e18]` and assert `wrsETH.balanceOf(depositor) > 0` after each deposit — this assertion will fail for all inputs in that range.