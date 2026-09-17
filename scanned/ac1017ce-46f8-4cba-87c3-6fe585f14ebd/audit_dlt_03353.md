# [M] The First User To Borrow a Particular Token Can Drain Funds In MarginSwap by Making An Undercollateralized Borrow Using Flash Loans

## Summary
Severity: Medium
Chain: Smart contract
Component: 2021-04-marginswap
Published: 2021-04-07
Source: https://github.com/code-423n4/2021-04-marginswap-findings/issues/66
Type: code-finding

## Details
# Handle

jvaqa


# Vulnerability details

The First User To Borrow a Particular Token Can Drain Funds In MarginSwap by Making An Undercollateralized Borrow Using Flash Loans

## Impact

This attack can be performed with any two ERC20 tokens, where one of them has not yet been borrowed on MarginSwap.
Since any newly added token must first be loaned before it can be borrowed, there will always be a window of time where this attack is possible for any newly added asset.
The magnitude of the attack will be limited by the size of MarginSwap.CrossMarginAccounts.tokenCaps[borrowToken], but could potentially allow an attacker to drain one particular token from MarginSwap if it has been lent but not yet borrowed.

## Proof of Concept

For the sake of argument, let's assume two ERC20 tokens called Token0 and Token1, who have a current market price of 1:1.

Expected Behavior:
Alice can only borrow 900 Token1 if she puts up 1,000 Token0 as collateral.

Actual Behavior:
Using this attack, Alice can borrow 9,000 Token1 when using 1,000 Token0 as collateral. She can leave her 1,000 Token0 behind in MarginSwap, and sell the 9,000 Token1 for an 8,000 token profit.
It should be noted that this attack can be larger than what is shown here: we demonstrate a 10x attack for simplicity, but it only depends on how much liquidity is in the Uniswap pool, determining how much it will cost to skew the price.

(0) Alice begins with 1,000 Token0 and 1,000 Token1
(1) Alice calls AliceAttackerContract.functionOneOfTwo(), which performs the following calls:
  (1.1) Calls Token0.approve(MarginSwap, UINT256MAX) to allow MarginSwap to spend her Token0
  (1.2) Calls MarginSwap.MarginRouter.crossDeposit(Token0Address, 1000 * 1e18)
(2) Alice waits for n + 1 blocks to pass, where n is specified in MarginSwap.CrossMarginTrading.coolingOffPeriod (currently set at 20 blocks)
(3) Alice calls AliceAttackerContract.functionTwoOfTwo(), which performs the following calls:
  (3.1) Flashloan Token1
  (3.2) Trade Token1 for Token0 on Uniswap to make Token1's price on Uniswap appear cheaper. For argument's sake let's skew the price to 10:1
  (3.3) Calls Token1.approve(MarginSwap, UINT256MAX) to allow MarginSwap to spend her Token1
  (3.3) Call MarginRouter.crossBorrow(Token1Address, 9000 * 1e18);
  (3.4) Call MarginRouter.crossWithdraw(Token1Address, 9000 * 1e18);
  (3.5) Trade Token0 for Token1 on Uniswap to return the Uniswap price to market price, minus fees
  (3.6) Repay the Flashloan of Token1
(4) Alice ends with 10,000 Token1 (minus Uniswap fees). Since we assumed Token0 and Token1 had the same market price for the sake of argument, Alice has a profit of 8,000 Token1 minus Uniswap fees, and MarginSwap has lost 8,000 Token1.

The various defenses that MarginSwap has employed against flashLoans are all bypassed:
(a) MarginSwap employed noIntermediary() on MarginSwap.CrossMarginLiquidation.liquidate() in order to prevent the liquidation function from being called by a contract. However, this defense does not prevent crossDeposit() or crossBorrow() from being called by a contract.
(b) The coolingOffPeriod is bypassed, since the flashLoan price manipulation can occur at the moment of withdrawal, and the coolingOffPeriod is only triggered upon deposit, so you can split the deposit and withdrawal into two transactions that are separated by at least coolingOffPeriod number of blocks.
(c) UPDATE_MIN_PEG_AMOUNT and UPDATE_MAX_PEG_AMOUNT are bypassed, since if this is the first borrow for Token1, then MarginSwap.PriceAware.getCurrentPriceInPeg() simply returns the current price from Uniswap, not an exponential moving average, and does not consult UPDATE_MIN_PEG_AMOUNT and UPDATE_MAX_PEG_AMOUNT at all.
(d) MarginSwap.Lending.registerBorrow check is bypassed. The check is "meta.totalLending >= meta.totalBorrowed", but this is a global check that only ensures that the contract as a whole has sufficient Token1 to fund Alice's borrow. If users have lent Token1 to MarginSwap but no one has borrowed it yet, then Alice simply needs to ensure that she does not borrow more than those users have lent.
(e) MarginSwap.CrossMarginTrading._registerBorrow check is bypassed. The check is "tokenCaps[borrowToken] >= totalShort[borrowToken]". Since Alice does not need to make a huge borrow for her attack to succeed, even a conservative initial borrowCap can be bypassed for at least some profit.

## Recommended Mitigation Steps

The best solution is to use Uniswap's built in TWAP, and to take your first measurement from it when you add a new token, rather than at the time of the first borrow of that token.
Using a price oracle that is internal to MarginSwap leads to less accurate prices, which is especially problematic for an application that features lending/borrowing. If MarginSwap is not widely used or if it features a lesser used token, the price oracle will be innacurate and will lead to attacks.
Since Uniswap already has TWAPs built in, there is no reason not to utilize them, since they will be far more accurate.
