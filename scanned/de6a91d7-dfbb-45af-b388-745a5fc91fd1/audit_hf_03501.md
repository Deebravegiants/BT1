# [M] Incorrect calculations in deposit

## Summary
Severity: Medium
Contest weight: 0.5185
Dataset id: 19186
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The vulnerability is an accounting mis‑calculation in the deposit() routine of the TokenisableRange contract. The function deducts an "uncompounded" fee from the amounts a user declares (n0 and n1) but it computes that fee using the raw user inputs instead of the amounts that will actually be deposited after they are adjusted to the current market price ratio. Because the pool’s price may require a different proportion of token0 to token1 than the user supplied, the fee is applied to a mismatched quantity. When the user later withdraws the liquidity without any market movement, the contract uses the market‑adjusted amounts to calculate the return, so the fee that was taken based on the original inputs is not fully reimbursed. The result is a small but deterministic loss of the fee component – the user sees fewer tokens returned than expected, effectively causing funds to disappear. This bug manifests whenever a depositor provides token amounts that are not already proportional to the pool’s price and the fee parameters are non‑zero. It affects any participant who deposits liquidity and expects a symmetric withdraw (i.e., the same amount back when no price change occurs). The issue was uncovered during a Code4rena audit by analysing the fee‑adjustment logic and noticing that the proportionality check uses the wrong basis. It is hard to spot because the contract still passes basic slippage checks and the loss is only visible after a full deposit‑withdraw cycle, which many users may not perform in testing. Conceptually, the fix is to first normalize the user‑provided amounts to the pool’s current ratio, then calculate the fee on those normalized values, ensuring that the fee taken and the fee returned are based on the same underlying quantity. This aligns the accounting with the intended business logic that a deposit and immediate withdrawal (excluding fees) should be loss‑less, and eliminates the class of bug known as “proportional fee mis‑calculation”. From a user’s perspective the UI would show the deposited amount, but after withdrawal the balance would be slightly lower than expected, contradicting the expectation that “what I put in should come out unchanged when no fees are applied”.

## Proof of Concept
Generally speaking, functions in a protocol should be designed symmetrically. For example in a DEX, when swap X to Y and then immediately swap Y to X, when excluding fees, the user won’t loss any funds. In this TokenisableRange.sol case, when a user deposits some funds, if the user withdraw it immediately, and when there is no market condition change and exclude fees, the amount the user can obtained should be same as the deposit value.

However, this is not the case in deposit() function. In deposit(), a user will input the amount he/she want to deposit, a uncompound fee may subtracted from that amount, and the rest of the amount will be deposited, and LP tokens will be transferred to the user. When withdraw, the user burn the LP token, and obtain the corresponding liquidity and uncompounded fee. As stated above, when no market change and exclude any fees, the liquidity and uncompounded fee a user can get should be the same as paid in deposit(). The issue is in these lines:

```solidity
if (fee0 + fee1 > 0 && (n0 > 0 || fee0 == 0) && (n1 > 0 || fee1 == 0)) {
    address pool = V3_FACTORY.getPool(
        address(TOKEN0.token),
        address(TOKEN1.token),
        feeTier * 100
    );
    (uint160 sqrtPriceX96, , , , , , ) = IUniswapV3Pool(pool).slot0();
    (uint256 token0Amount, uint256 token1Amount) = LiquidityAmounts
        .getAmountsForLiquidity(
            sqrtPriceX96,
            TickMath.getSqrtRatioAtTick(lowerTick),
            TickMath.getSqrtRatioAtTick(upperTick),
            liquidity
        );
    if (token0Amount + fee0 > 0)
        newFee0 = (n0 * fee0) / (token0Amount + fee0);
    if (token1Amount + fee1 > 0)
        newFee1 = (n1 * fee1) / (token1Amount + fee1);
    fee0 += newFee0;
    fee1 += newFee1;
    n0 -= newFee0;
    n1 -= newFee1;
}
```

The issue here is, the deducted uncompounded fee newFee0 and newFee1 are computed based on users input n0 and n1, but the user input n0 and n1 may not be as the same ratio correspond to the current market ratio. So in conclusion, the uncompounded fees is computed based on user input n0 and n1, the ratio between that n0 and n1 may not be the current ratio under current market condition, but later the actual deposit amounts are based on the current ratio and the minted LP token also based on that ratio, the current ratio is also used in withdraw, so it is this difference that result in a potential loss in uncompounded fee.

This may not obvious so let’s look at an example with solid numbers.

We assume such a condition. User input n0 = 415, n1 = 100, uncompounded fee0 f0 = 20, fee1 f1 = 5, under current market price and tick range token0Amount t0 = 4000, token1Amount t1 = 1000, t0 and t1 correspond to a liquidity L of 1000, and LP token total supply T is 2000.

Since f0 + f1 = 25 > 0 && n0 = 415 > 0 && n1 = 100 > 0, we will enter the first if statement to compute the deducted uncompounded fee. newFee0 = 415*20/(4000+20) = 415/201, newFee1 = 100*5/(1000+5) = 100/201, updated n0 = 415 - 415/201 = 412.9353234, updated n1 = 100 - 100/201 = 20000/201.

We will then make the deposit. Under current assumed market condition we can deposit n1 of 20000/201 and n0 of 80000/201 and obtain a new liquidity newL of 20000/201. The LP token amount we can get is newL/L*T = 40000/201. Note here n1 will all be deposited, deposited n0 is 80000/201 , which is larger than 95% of (n1 - newFee0), which is 95% of 412.9353234. So slippage check is satisfied.

In conclusion, in this deposit(), user specified n0 of 415 and n1 of 100, user have an actual deposit of n0 = 80000/201 and n1 of 20000/201, this corresponding to a liquidity of 20000/201, user also deposit a uncompounded fee, newFee0 is 415/201 and newFee1 is 100/201. User get back 40000/201 LP token. Now updated fee0 = 20 + 415/201 = 1475/67, and updated fee1 = 5 + 100/201 = 1105/201. Updated total liquidity is 1000 + 20000/201 = 1099.502488, and updated LP token supply is 442000/201.

Now user wants to withdraw. He will burn all his LP token, so the removedLiquidity he can get is (40000/201)/(442000/201)*1099.502488 = 20000/201, this is same as the liquidity got in deposit(). For uncompounded fee, obtained fee0 = (40000/201)/(442000/201)*1475/67 = 1.9923, obtained fee1 = (40000/201)/(442000/201)*1105/201 = 100/201. We can see the fee1 got back is exactly the same, but the fee0 different, deposited 415/201 = 2.0647 but only get back 1.9923, so the user will incur a loss.

As mentioned before, the loss in uncompounded fee here is due to use user input n0 and n1 here, which may not be proportional to the actual deposit amount.

## Recommendation
The protocol should first calculate a proportioned n0 and n1 based on user inputs, then compute uncompounded fee based on that. Take the example above, user inputs n0 = 415 and n1 = 100, the protocol should calculate that the proportioned n0 = 400 and n1 = 100 under current condition. Then the fee should be calculated based on the n0 of 400 and n1 of 100.

Removed `addDust` mechanism, replaced by `depositExactly` in TR.  
PR: <https://github.com/GoodEntry-io/ge/pull/8>
