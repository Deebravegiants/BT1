# [M] `reLPContract.reLP

## Summary
Severity: Medium
Contest weight: 0.5240
Dataset id: 19158
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
`RdpxV2Core.bond()` calls `reLPContract.reLP()` at the end of the bonding to adjust the LP for the rDPX/ETH pool and swap ETH for rDPX. Within `reLPContract.reLP()`, it first calls `removeLiquidity()` to remove liquidity (rDPX and ETH), followed by `swapExactTokensForTokens()` and `addLiquidity()`.

However, the issue is that an attacker has control over `RdpxV2Core.bond()` and can use it to indirectly call `reLPContract.reLP()`. That means the attacker can basically frontrun/backrun `reLP()` without a mempool. It also reduces the attack cost as attacker does not pay high gas to frontrun it.

One may argue that the slippage protection is in place, but that only makes it less profitable and would not help in this case because the attacker is able to increase the trade size of the UniswapV2 transactions. That is because the attacker can adjust the bonding amount to increase the amount of liquidity removed by `reLP()` (and also swap/add liquidity), allowing the attacker to craft a profitable sandwich attack.

It is not recommended to allow users to have indirect control over the UniswapV2 transaction in `reLPContract`.

```solidity
function bond(
    uint256 _amount,
    uint256 rdpxBondId,
    address _to
) public returns (uint256 receiptTokenAmount) {

    ...
    // @audit an attacker can indirectly trigger this to perform a large trade and sandwich attack it
    // reLP
    if (isReLPActive) IReLP(addresses.reLPContract).reLP(_amount);
```

## Proof of Concept
An attacker can perform a sandwich attack as follows:

  1. Perform a flash loan to borrow ETH.
  2. Use the borrowed ETH to perform a ETH-to-rDPX swap on the UniswapV2 rDPX/ETH pool. This is to increase the price of rDPX before `reLPContract.reLP()`.
  3. Call `rdpxV2Core.bond()` to indirectly trigger `reLPContract.reLP()`, which will `removeLiquidity()`, causing it to receive lesser rDPX due to the price manipulation.
  4. `reLPContract.reLP()` will then `swapExactTokensForTokens()` to swap ETH-to-rDPX using ETH from removed liquidity. This further increases price of rDPX.
  5. `addLiquidity()` is then called by `reLPContract.reLP()` to return part of the liquidity into the pool.
  6. Attacker now swaps rDPX back to ETH to realize profit from the attack and pays back the flash loan.

## Recommendation
Remove `reLPContract.ReLP()` from `bond()` and trigger separately to prevent user access to it.

The re-LP contract and process will be modified.

I would have liked to see a Coded POC.

Removing Liquidity is not as simple to exploit as swap.

UniV2 Code is as follows:  
<https://github.com/Uniswap/v2-core/blob/ee547b17853e71ed4e0101ccfd52e70d5acded58/contracts/UniswapV2Pair.sol#L144-L155>

Offering Pro Rata Distribution

In lack of a coded POC

The maximum skimmable is the delta excess value in the UniV2 Reserves vs the value that the caller has to pay to imbalance them.

The cost of imbalancing and the nature of it + the fact that other people would have ownership of the LP token means that profitability is dependent on those factors, which IMO have not been properly factored in.

In the presence of a Coded POC as part of the original submission, I would have considered a High Severity.

In lack of it, Medium Severity for Skimming the excess value seems more appropriate.

Hi @Alex the Entreprenerd, 

I understand your judgement as you have raised valid points, though the circumstances here are different (explained below), which make it more profitable as compared to a typical sandwich attack on removeLiquidity().

**1\. Coded POC**  
Below is the printout from the POC, which shows it is more than just skimming of excess value (profit of 42.79 ETH using 1000 ETH flash loan vs minimal cost in point 2 below). For your reference, I have uploaded it [here](https://gist.github.com/peakbolt/f2d9a44714b1a2a693debea737128696).
    
   
     --------------  setup copied from testReLpContract() ------------
      -------------- 1. attacker perform first swap to get rDPX with flashloaned WETH ------------
      attacker weth balance (initial) : 10000000000000000000000 [from flashloan]
      attacker rdpx balance (initial) : 0 
      attacker weth balance (after 1st swap): 0 
      attacker rdpx balance (after 1st swap): 33799781371440793668463
      rDPX price in WETH (after 1st swap): 435429977934145959 
      -------------- 2. Attacker triggers bond() that indirectly perform removeLiquidity() in reLPContract.reLP() ------------
      rDPX price in WETH (after bond): 440827346696573406 
      -------------- 3. Attacker performs 2nd swap rDPX back to WETH and profit ------------
      attacker weth balance (after 2nd swap): 10042795347724107931994 
      attacker rdpx balance (after 2nd swap): 0
      attacker profit in WETH (after repaying flashloan): 42795347724107931994

**2\. Cost of imbalancing** There are 3 main attack cost implicitly mentioned in the original submission. Based on the POC, they are ~11 ETH, minimal as compared to the 42.79 ETH profit.

  * Flash loan cost - as mentioned, use of flash loan for WETH in POC. If we take Aave as a reference, flash loan fee is 0.09% of flash loan amount, which will be 9 ETH based on POC, lower than the 42.79 ETH profit.
  * Gas cost - as mentioned this attack does not involve mempool to frontrun, so attacker does not need to pay high gas fee.
  * Bonding cost - obviously rDPX and ETH are required to trigger bond(), this is negligible as it can be recouped by redeeming/selling the bonded dpxETH. If we take Aave ETH borrow cost at a conservative 2% APY for 1e20 dpxETH bonding amount, that will be 2 ETH, which is even lower than flash loan fee.


**3\. Control over amount of LP tokens to remove** As mentioned in my submission, in this case, the attacker has control of the trade size of removeLiquidity() via bond() amount. By increasing the bond amount, which increase amount of LP tokens to remove, the attacker can increase the profitability of the attack.

**4\. During the bootstrap phase, majority of LP holders are dopex funds/partners** The docs stated that during bootstrap phase, Dopex Treasury funds and Partners will partake in the dpxETH bonding first to ensure sufficient dpxETH in circulation. In addition, the backing reserve will be used to seed the liquidity for the Uniswap V2 Pool. So during that period, there are little other LP holders. I did not state this in submission as it is already in the docs.  
<https://dopex.notion.site/rDPX-V2-RI-b45b5b402af54bcab758d62fb7c69cb4> (see Launch Details)

@peakbolt 

  * What’s the value in Pool?
  * Can you repeat the attack more than once?
  * What’s the profit / value drained per iteration?
  * What’s the threshold of TVL before the attack is profitable given 30BPS swap fees?
 

Hi @Alex the Entreprenerd, 

I have adjusted the POC to a liquidity pool value of ~800 ETH with flashloan attack amount of 15e20 and ran it to provide the answers below. Used 800ETH TVL as the assumed amount to bootstrap, judging by the lower range of TVL in the top uniswap pools. Note that the initial TVL value in the test suite is actually 4000 ETH.  
See link for updated poc: <https://gist.github.com/peakbolt/a8fdbe18759ac2e25d15716af6faa76b>.

  1. Yes, it is possible to repeat the attack more than once by bonding multiple times to trigger consecutive removal of liquidity after imbalancing the pool. 
  2. Printout for the updated poc below, shows an attack with 5 `bond()` iterations. 
  3. Beyond 5 `bond()` will hit a revert as there will be insufficient WETH collateral in `PerpetualAltanticVault` for purchase of put options (during bonding). 
  4. The attacker can workaround that by waiting for users to deposit more WETH into PerpetualAltanticVault before carrying out the attack.


    Total Liquidity (in WETH) for RDPX/WETH UniswapV2 Pool (before attack): 804803971980485176292 
    attacker weth balance (initial) : 1500000000000000000000 [from flashloan]
    attacker rdpx balance (initial) : 0
    bond() Iteration 1
    bond() Iteration 2
    bond() Iteration 3
    bond() Iteration 4
    bond() Iteration 5
    attacker profit in WETH (after repaying flashloan): 22067892940781745930

  2. Based on the poc (~800ETH TVL), the attack with 5 iterations will gain ~22 ETH (inclusive of swap fees as shown in POC using Arb mainnet fork). 
  3. For 800 ETH TVL, the flash loan cost for attack is lower at 1.35 ETH (0.09% of 15e20 ETH)
  4. After flash loan cost profit will be 22-1.35 = 20.65 ETH
  5. That works out to be 20.65/800 ETH = ~2.58% profit/TVL. 
  6. Per iteration will be 0.516% profit/TVL.
  7. For bonding, it will require upfront capital of 1e20 WETH/iteration to bond the dpxETH, which can be recouped by selling the dpxETH later on. To keep it simple, I have omitted the loan cost for this and assume attacker has the capital. Otherwise, attacker can get a loan and reduces attack profit. 
  8. As for the TVL threshold, I have tried lower TVL at 400 ETH and attack is still viable, with a profit 11.32 ETH (12.04 ETH - flash loan cost of 0.72 ETH). Did not try lower as I assume protocol will not bootstrap lower than that. Though profit is still possible to a certain extent, but likely insignificant.


The finding shows that the attacker has access to the “button”, this allows them to cause the contract to auto-rebalance.

The auto-rebalancing is part of the “button” that attack can trigger.

Initially I believed that the attacker only had control over the amounts from remove liquidity, which by definition will give pro-rata of the tokens.

The pro-rata can be manipulated based on attacking the `X * Y = k` uniswap invariant to have the contract take a loss that is relative to the new spot balance, vs the fair LP pricing.

That was Medium Severity imo and most Judges would agree with me, however, after talking with 2 more judges, we agreed that the code also impacts the rebalancing, done via `swapExactTokensForTokens` meaning that the attacker is not only causing the “skimming” of the LP token value, they are able to influence the swap via `swapExactTokensForTokens`.

However, upon further inspection, that is protected by the Oracle Pricing, which could be argued to protect against it.

That said, the default slippage protection is 50 BPS, which is above the 30BPS avg cost of a swap on UnIV2, the oracles also can have drift which in general should make the cost of backrunning sustainable.

The profit of the attack would come due to: -> Swap taking a Loss -> generally seen as Med but since it’s repeatable High is acceptable -> Ability to trigger the Withdrawal at any time, which causes the Pro-Rata received `X * Y` being less valuable than the fair valuation of the LP Token.

This means that under most circumstances, a risk free trade is available for attacker at the detriment of the `reLP` contract, leading me to believe High Severity to be appropriate.

However, given the circumstances, and given the original submission did not contain the POC, also considering that the POC shows an impact of 2% of funds, I’m maintaining Medium Severity due to the POC not being present in the original submission.
