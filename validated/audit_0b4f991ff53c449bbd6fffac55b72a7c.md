Audit Report

## Title
Dust Deposit Mints Zero rsETH, Permanently Losing User Funds - (File: contracts/pools/RSETHPoolV3.sol)

## Summary
`RSETHPoolV3.deposit` (both ETH and token paths) guards only against `amount == 0` but imposes no minimum deposit floor. For any dust-sized deposit, integer division in `viewSwapRsETHAmountAndFee` silently truncates `rsETHAmount` to zero. The user's ETH or tokens are transferred into the pool, `wrsETH.mint(msg.sender, 0)` is called (which succeeds silently in OpenZeppelin ERC20), and the deposited value is permanently absorbed into the pool's bridgeable balance with no user claim.

## Finding Description
Both public `deposit` entry points check only for strict zero: [1](#0-0) [2](#0-1) 

The rsETH amount is computed in `viewSwapRsETHAmountAndFee`: [3](#0-2) [4](#0-3) 

Because `rsETHToETHrate` is ~1.05e18, any `amountAfterFee` where `amountAfterFee * 1e18 < rsETHToETHrate` (e.g., 1 wei ETH) produces `rsETHAmount = 0` via integer truncation. The `limitDailyMint` modifier computes this same zero value and adds it to `dailyMintAmount` as a no-op: [5](#0-4) 

Execution then falls through to the function body, which passes the `amount == 0` guard, and calls: [6](#0-5) [7](#0-6) 

OpenZeppelin's `ERC20._mint` does not revert on a zero amount. For the ETH path, the deposited ETH remains in the contract and is included in `getETHBalanceMinusFees()`, making it available for bridging via `moveAssetsForBridging`. For the token path, `safeTransferFrom` executes at L284 before `rsETHAmount` is computed, so tokens are already transferred in before the zero-mint occurs: [8](#0-7) 

`feeEarnedInETH += 0` records no fee, no rsETH is minted, and the deposited value is silently absorbed into the pool's bridgeable balance with no on-chain claim for the depositor. By contrast, `LRTDepositPool.sol` enforces a `minAmountToDeposit` floor: [9](#0-8) 

`RSETHPoolV3` has no equivalent guard.

## Impact Explanation
A user who deposits a dust amount permanently loses their ETH or tokens. The funds flow into the pool's bridgeable balance and are eventually sent to L1 with no attribution to the depositor and no recovery path. This constitutes **"Contract fails to deliver promised returns"** (Low) at minimum — the contract accepts a non-zero deposit and delivers zero rsETH — and is also consistent with **"Permanent freezing of funds"** (Critical) from the depositor's perspective, since the deposited value is irrecoverably absorbed. The submitted claim conservatively rates this Low.

## Likelihood Explanation
Requires a user to submit a dust-sized deposit. Realistic triggers include: wrong decimal units in user input, a buggy or rounding front-end, or an automated integration computing a residual amount. No privileged role or special precondition is required — any unprivileged external caller can trigger this via the public `deposit` functions. Likelihood: **Low**.

## Recommendation
Add a post-calculation guard immediately after calling `viewSwapRsETHAmountAndFee` in both deposit paths, analogous to `LRTDepositPool`'s `minRSETHAmountExpected` check:

```solidity
if (rsETHAmount == 0) revert InvalidAmount();
```

Apply this at lines 258–259 (ETH path) and 286–287 (token path) in `RSETHPoolV3.sol`.

## Proof of Concept
1. `rsETHToETHrate` = 1.05e18 (rsETH at a 5% premium to ETH).
2. User calls `RSETHPoolV3.deposit{value: 1}("")` (1 wei ETH).
3. `limitDailyMint` modifier: `viewSwapRsETHAmountAndFee(1)` → `fee = 1 * 0 / 10_000 = 0`, `amountAfterFee = 1`, `rsETHAmount = 1 * 1e18 / 1.05e18 = 0`; `dailyMintAmount += 0` (no-op, no revert).
4. Function body: `amount = 1`, passes `if (amount == 0)` check.
5. `viewSwapRsETHAmountAndFee(1)` → `rsETHAmount = 0`, `fee = 0`.
6. `feeEarnedInETH += 0`.
7. `wrsETH.mint(msg.sender, 0)` — succeeds, emits `Transfer(address(0), user, 0)`.
8. User's 1 wei is in the pool's ETH balance; `getETHBalanceMinusFees()` includes it; user holds 0 rsETH with no recovery path.

**Foundry fuzz test plan:**
```solidity
function testFuzz_dustDepositMintsZero(uint256 amount) public {
    vm.assume(amount > 0 && amount < rsETHToETHrate / 1e18 + 1);
    uint256 balanceBefore = wrsETH.balanceOf(user);
    vm.deal(user, amount);
    vm.prank(user);
    pool.deposit{value: amount}("");
    assertEq(wrsETH.balanceOf(user), balanceBefore); // user receives 0 rsETH
    assertGt(address(pool).balance, 0);              // ETH absorbed into pool
}
```

### Citations

**File:** contracts/pools/RSETHPoolV3.sol (L119-124)
```text
        if (dailyMintAmount + rsETHAmount > dailyMintLimit) {
            revert DailyMintLimitExceeded();
        }

        dailyMintAmount += rsETHAmount;
        _;
```

**File:** contracts/pools/RSETHPoolV3.sol (L256-256)
```text
        if (amount == 0) revert InvalidAmount();
```

**File:** contracts/pools/RSETHPoolV3.sol (L262-262)
```text
        wrsETH.mint(msg.sender, rsETHAmount);
```

**File:** contracts/pools/RSETHPoolV3.sol (L282-282)
```text
        if (amount == 0) revert InvalidAmount();
```

**File:** contracts/pools/RSETHPoolV3.sol (L284-290)
```text
        IERC20(token).safeTransferFrom(msg.sender, address(this), amount);

        (uint256 rsETHAmount, uint256 fee) = viewSwapRsETHAmountAndFee(amount, token);

        feeEarnedInToken[token] += fee;

        wrsETH.mint(msg.sender, rsETHAmount);
```

**File:** contracts/pools/RSETHPoolV3.sol (L299-308)
```text
    function viewSwapRsETHAmountAndFee(uint256 amount) public view returns (uint256 rsETHAmount, uint256 fee) {
        fee = amount * feeBps / 10_000;
        uint256 amountAfterFee = amount - fee;

        // rate of rsETH in ETH
        uint256 rsETHToETHrate = getRate();

        // Calculate the final rsETH amount
        rsETHAmount = amountAfterFee * 1e18 / rsETHToETHrate;
    }
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

**File:** contracts/LRTDepositPool.sol (L657-659)
```text
        if (depositAmount == 0 || depositAmount < minAmountToDeposit) {
            revert InvalidAmountToDeposit();
        }
```
