Audit Report

## Title
Zero-Output Token Deposit Permanently Loses Depositor Funds Due to Missing `rsETHAmount == 0` Guard - (File: contracts/pools/RSETHPoolV3.sol)

## Summary
The token-deposit variant of `deposit(address token, uint256 amount, string referralId)` in `RSETHPoolV3`, `RSETHPoolV3ExternalBridge`, and `RSETHPoolV3WithNativeChainBridge` transfers the depositor's token into the pool before computing `rsETHAmount`. When WETH is the deposit token and `rsETHToETHrate > 1e18`, depositing 1 wei produces `rsETHAmount = 0` via integer truncation. The token is transferred in, zero wrsETH is minted, and the depositor has no recovery path.

## Finding Description
`WETHOracle.getRate()` always returns exactly `1e18`. The token-deposit variant of `viewSwapRsETHAmountAndFee` computes:

```solidity
rsETHAmount = amountAfterFee * tokenToETHRate / rsETHToETHrate;
```

With WETH as the token, `tokenToETHRate = 1e18`. When `rsETHToETHrate > 1e18` (e.g., `1.05e18` after yield accrual), depositing `amount = 1` with `feeBps = 0` yields:

```
rsETHAmount = 1 * 1e18 / 1.05e18 = 0  (Solidity integer truncation)
```

The `deposit` function guards only against `amount == 0` but not `rsETHAmount == 0`:

```solidity
if (amount == 0) revert InvalidAmount();
IERC20(token).safeTransferFrom(msg.sender, address(this), amount);  // 1 wei transferred in
(uint256 rsETHAmount, uint256 fee) = viewSwapRsETHAmountAndFee(amount, token);  // returns (0, 0)
feeEarnedInToken[token] += fee;   // += 0
wrsETH.mint(msg.sender, rsETHAmount);  // mint(msg.sender, 0) — does NOT revert in OZ ERC20
```

OpenZeppelin's `_mint(address, 0)` does not revert; it emits a `Transfer` event for 0 and returns. The `limitDailyMint` modifier also passes silently because `0 + 0 > dailyMintLimit` is always false. The transaction succeeds, 1 wei WETH is in the pool, and the depositor holds 0 wrsETH. There is no `withdrawDeposit`, no refund path, and no minimum-output parameter on the token deposit path. The 1 wei enters `getTokenBalanceMinusFees` and will be bridged to L1 via `bridgeTokens`.

The identical pattern is present in `RSETHPoolV3ExternalBridge.deposit(address,uint256,string)` and `RSETHPoolV3WithNativeChainBridge.deposit(address,uint256,string)`.

## Impact Explanation
A depositor's token is permanently frozen from their perspective — they receive nothing in return and have no on-chain mechanism to reclaim it. This matches **Low: Contract fails to deliver promised returns** (zero wrsETH minted for a non-zero deposit) and technically also **Critical: Permanent freezing of funds** (the deposited wei is irrecoverable by the depositor). The per-transaction loss is bounded to dust (at most 1 wei of WETH per transaction when `rsETHToETHrate` is just above `1e18`), making the practical financial impact negligible. Severity is assessed as **Low**.

## Likelihood Explanation
The condition `rsETHToETHrate > 1e18` is the normal operating state once rsETH has accrued any yield — it is always present in production. The trigger requires depositing exactly 1 wei of WETH (or a similarly tiny amount below `rsETHToETHrate / 1e18`). A rational user would not do this intentionally, but a buggy integration, a UI rounding error, or a deliberate dust-deposit could trigger it. The condition is permanently present and repeatable.

## Recommendation
Add a post-computation guard in `deposit` (and equivalently in all pool variants) immediately after computing `rsETHAmount` and before `wrsETH.mint`:

```solidity
if (rsETHAmount == 0) revert InvalidAmount();
```

Apply the same fix to `RSETHPoolV3`, `RSETHPoolV3ExternalBridge`, `RSETHPoolV3WithNativeChainBridge`, and any other pool variants (`RSETHPool`, `RSETHPoolNoWrapper`). Alternatively, add the guard inside `viewSwapRsETHAmountAndFee` so all callers benefit automatically.

## Proof of Concept
```solidity
// Foundry fork/unit test
// Preconditions:
//   rsETHOracle.getRate() returns 1.05e18 (normal post-yield state)
//   WETH is a supported token with WETHOracle (returns 1e18)
//   feeBps = 0

uint256 wethBefore = WETH.balanceOf(address(pool));
uint256 wrsETHBefore = wrsETH.balanceOf(depositor);

vm.startPrank(depositor);
WETH.approve(address(pool), 1);
pool.deposit(address(WETH), 1, "");  // succeeds — no revert
vm.stopPrank();

assertEq(WETH.balanceOf(address(pool)) - wethBefore, 1);       // 1 wei WETH transferred in
assertEq(wrsETH.balanceOf(depositor) - wrsETHBefore, 0);       // 0 wrsETH minted
// depositor's 1 wei WETH is permanently unrecoverable
```