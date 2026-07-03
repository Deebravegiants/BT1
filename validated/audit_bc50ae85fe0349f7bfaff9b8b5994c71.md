Audit Report

## Title
Missing Output Amount Validation Allows Permanent Loss of Deposited Assets on Zero-Output Deposits - (File: contracts/pools/RSETHPoolV3.sol)

## Summary
The `deposit` functions in `RSETHPoolV3` and `RSETHPoolNoWrapper` validate only that the input `amount != 0`, but never validate that the computed `rsETHAmount > 0`. When a user deposits a sufficiently small amount, integer division in `viewSwapRsETHAmountAndFee` truncates `rsETHAmount` to zero. The user's assets are transferred to the pool, zero rsETH/wrsETH is minted or transferred back, and the deposited `amountAfterFee` is not tracked in any fee or accounting variable, leaving it permanently inaccessible to the depositor.

## Finding Description
In `RSETHPoolV3.deposit(address token, uint256 amount, string referralId)` (L271–293), the only input guard is:

```solidity
if (amount == 0) revert InvalidAmount();
```

The token transfer occurs before the output is computed:

```solidity
IERC20(token).safeTransferFrom(msg.sender, address(this), amount);
(uint256 rsETHAmount, uint256 fee) = viewSwapRsETHAmountAndFee(amount, token);
feeEarnedInToken[token] += fee;
wrsETH.mint(msg.sender, rsETHAmount);
```

Inside `viewSwapRsETHAmountAndFee` (L315–335):

```solidity
fee = amount * feeBps / 10_000;
uint256 amountAfterFee = amount - fee;
uint256 rsETHToETHrate = getRate();
uint256 tokenToETHRate = IOracle(supportedTokenOracle[token]).getRate();
rsETHAmount = amountAfterFee * tokenToETHRate / rsETHToETHrate;
```

When `amountAfterFee * tokenToETHRate < rsETHToETHrate`, Solidity integer division truncates `rsETHAmount` to `0`. The consequences are:

- `feeEarnedInToken[token] += fee` records only the fee portion (which is also 0 when `feeBps = 0` or when `amount * feeBps / 10_000 = 0`).
- `wrsETH.mint(msg.sender, 0)` is a no-op; the user receives nothing.
- The `amountAfterFee` portion is not tracked in `feeEarnedInToken[token]`, so it is not withdrawable via `withdrawFees`.
- `getTokenBalanceMinusFees(token)` returns `balanceOf(address(this)) - feeEarnedInToken[token]`, which includes the stuck `amountAfterFee`. This amount is accessible only to `BRIDGER_ROLE` via `moveAssetsForBridging`, not to the depositor.

The same pattern exists in:
- `RSETHPoolV3.deposit(string referralId)` (L246–265): ETH path, `rsETHAmount = amountAfterFee * 1e18 / rsETHToETHrate`; ETH is stuck, `wrsETH.mint(msg.sender, 0)` is a no-op.
- `RSETHPoolNoWrapper.deposit(address token, uint256 amount, string referralId)` (L250–271): `rsETH.safeTransfer(msg.sender, 0)` is a no-op; token is stuck.
- `RSETHPoolNoWrapper.deposit(string referralId)` (L231–244): ETH path, same truncation.

The `limitDailyMint` modifier in `RSETHPoolV3` (L96–125) also calls `viewSwapRsETHAmountAndFee` and checks `dailyMintAmount + rsETHAmount > dailyMintLimit`. When `rsETHAmount = 0`, this check passes without reverting, so the modifier provides no protection.

## Impact Explanation
**Critical — Permanent freezing of user funds.** A user who deposits a small but non-zero amount receives zero rsETH/wrsETH. Their deposited `amountAfterFee` is held by the pool contract and is not tracked in any accounting variable accessible to the user. There is no `withdrawFees`, `reclaim`, or any other user-callable function that returns these funds. The depositor has no reclaim path. The funds are permanently inaccessible to the depositor, satisfying the "Permanent freezing of funds" critical impact class.

## Likelihood Explanation
Any unprivileged external caller can trigger this by depositing a sufficiently small amount. For the ETH path in `RSETHPoolV3`, the threshold is `amountAfterFee < rsETHToETHrate / 1e18`. Since `rsETHToETHrate` is expressed in 1e18 units (e.g., `1.05e18`), depositing 1 wei of ETH satisfies the condition. For the token path, the threshold is `amountAfterFee < rsETHToETHrate / tokenToETHRate`. As rsETH accrues value over time, `rsETHToETHrate` increases, raising the minimum deposit required to avoid zero output. No special permissions, front-running, or external conditions are required. The condition is reachable by any user on any supported chain where these contracts are deployed.

## Recommendation
Add an explicit output amount check immediately after computing `rsETHAmount` in all deposit functions, before any asset transfer occurs (or at minimum before minting/transferring output):

```solidity
(uint256 rsETHAmount, uint256 fee) = viewSwapRsETHAmountAndFee(amount, token);
if (rsETHAmount == 0) revert InvalidAmount();
```

Alternatively, add a `minRsETHAmountExpected` parameter to all deposit functions so callers can enforce a slippage floor, consistent with the `minRSETHAmountExpected` guard already present in `LRTDepositPool.depositAsset`. For the token path in `RSETHPoolV3`, the `safeTransferFrom` should also be moved to after the output validation to avoid transferring assets that will yield zero output.

## Proof of Concept
**Scenario (RSETHPoolV3 token deposit, feeBps = 0):**

1. `rsETHToETHrate = 1.05e18` (rsETH worth 1.05 ETH), `tokenToETHRate = 1e18`.
2. User calls `RSETHPoolV3.deposit(token, 1, "")` depositing 1 wei of the token.
3. `limitDailyMint` modifier calls `viewSwapRsETHAmountAndFee(1, token)`: `rsETHAmount = 1 * 1e18 / 1.05e18 = 0`. Check `dailyMintAmount + 0 > dailyMintLimit` passes (no revert).
4. `amount == 0` check passes (amount = 1).
5. `IERC20(token).safeTransferFrom(msg.sender, address(this), 1)` — 1 wei transferred to pool.
6. `viewSwapRsETHAmountAndFee(1, token)` returns `(0, 0)`.
7. `feeEarnedInToken[token] += 0` — no fee recorded.
8. `wrsETH.mint(msg.sender, 0)` — no-op, user receives nothing.
9. `getTokenBalanceMinusFees(token)` = `1 - 0 = 1` — the 1 wei is in the bridgeable balance, accessible only to `BRIDGER_ROLE`, not to the depositor.

**Foundry fuzz test plan:**

```solidity
function testFuzz_zeroOutputDeposit(uint256 amount) public {
    vm.assume(amount > 0 && amount < rsETHToETHrate / tokenToETHRate);
    uint256 balanceBefore = token.balanceOf(user);
    vm.prank(user);
    pool.deposit(address(token), amount, "");
    uint256 balanceAfter = token.balanceOf(user);
    assertEq(wrsETH.balanceOf(user), 0); // user received nothing
    assertLt(balanceAfter, balanceBefore); // user lost tokens
    assertEq(pool.feeEarnedInToken(address(token)), 0); // not tracked as fees
}
``` [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3) [5](#0-4)

### Citations

**File:** contracts/pools/RSETHPoolV3.sol (L96-124)
```text
    modifier limitDailyMint(uint256 amount, address token) {
        if (block.timestamp < startTimestamp) {
            revert MintBeforeStartTimestamp();
        }

        uint256 rsETHAmount;

        // Calculate the amount of rsETH that will be minted
        if (token == ETH_IDENTIFIER) {
            (rsETHAmount,) = viewSwapRsETHAmountAndFee(amount);
        } else {
            (rsETHAmount,) = viewSwapRsETHAmountAndFee(amount, token);
        }

        uint256 currentDay = getCurrentDay();

        // If the current day is greater than the last mint day, reset the daily mint amount
        if (currentDay > lastMintDay) {
            lastMintDay = currentDay;
            dailyMintAmount = 0;
        }

        // Check if the daily mint amount plus the amount to mint is greater than the daily mint limit
        if (dailyMintAmount + rsETHAmount > dailyMintLimit) {
            revert DailyMintLimitExceeded();
        }

        dailyMintAmount += rsETHAmount;
        _;
```

**File:** contracts/pools/RSETHPoolV3.sol (L282-290)
```text
        if (amount == 0) revert InvalidAmount();

        IERC20(token).safeTransferFrom(msg.sender, address(this), amount);

        (uint256 rsETHAmount, uint256 fee) = viewSwapRsETHAmountAndFee(amount, token);

        feeEarnedInToken[token] += fee;

        wrsETH.mint(msg.sender, rsETHAmount);
```

**File:** contracts/pools/RSETHPoolV3.sol (L324-334)
```text
        fee = amount * feeBps / 10_000;
        uint256 amountAfterFee = amount - fee;

        // rate of rsETH in ETH
        uint256 rsETHToETHrate = getRate();

        // rate of token in ETH
        uint256 tokenToETHRate = IOracle(supportedTokenOracle[token]).getRate();

        // Calculate the final rsETH amount
        rsETHAmount = amountAfterFee * tokenToETHRate / rsETHToETHrate;
```

**File:** contracts/pools/RSETHPoolV3.sol (L371-373)
```text
    function getTokenBalanceMinusFees(address token) public view returns (uint256) {
        return IERC20(token).balanceOf(address(this)) - feeEarnedInToken[token];
    }
```

**File:** contracts/pools/RSETHPoolNoWrapper.sol (L260-270)
```text
        if (amount == 0) revert InvalidAmount();

        IERC20(token).safeTransferFrom(msg.sender, address(this), amount);

        (uint256 rsETHAmount, uint256 fee) = viewSwapRsETHAmountAndFee(amount, token);

        feeEarnedInToken[token] += fee;

        rsETH.safeTransfer(msg.sender, rsETHAmount);

        emit SwapOccurred(msg.sender, rsETHAmount, fee, referralId); // Add token address?
```
