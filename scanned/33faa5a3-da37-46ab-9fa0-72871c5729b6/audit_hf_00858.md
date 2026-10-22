# [M] Attacker Can Decide The Initial Ratio

## Summary
Severity: Medium
Contest weight: 0.5934
Dataset id: 2596
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
When the RA/CT is deposited in the AMM pool it must follow a pre defined ratio, but the attacker can see the pair has been deployed on uniV2 and make the first deposit (adding liquidity) and disrupt the intended ratio of the CT/RA.

1.) When depositing, the vault decides the ratio of the RA/CT to be deposited in the AMM pool ->
ntracts/libraries/VaultLib.sol#L204
```solidity
function __provideLiquidityWithRatio(
    State storage self,
    uint256 amount,
    IDsFlashSwapCore flashSwapRouter,
    address ctAddress,
    IUniswapV2Router02 ammRouter
) internal returns (uint256 ra, uint256 ct) {
    uint256 dsId = self.globalAssetIdx;
    uint256 ctRatio = __getAmmCtPriceRatio(self, flashSwapRouter, dsId);
    (ra, ct) = MathHelper.calculateProvideLiquidityAmountBasedOnCtPrice(amount, ctRatio);
    __provideLiquidity(self, ra, ct, flashSwapRouter, ctAddress, ammRouter, dsId);
}
```

```solidity
function __getAmmCtPriceRatio(State storage self, IDsFlashSwapCore flashSwapRouter, uint256 dsId)
    internal
    view
    returns (uint256 ratio)
{
    // This basically means that if the reserve is empty, then we use the default ratio supplied at deployment
    ratio = self.ds[dsId].exchangeRate() - self.vault.initialDsPrice;
    // will always fail for the first deposit
    try flashSwapRouter.getCurrentPriceRatio(self.info.toId(), dsId) returns (uint256, uint256 _ctRatio) {
        ratio = _ctRatio;
    } catch {}
}
```

If the pool is empty (it's the first liquidity addition) the ratio should follow the default ratio decided at development.

2.) But an attacker can frontrun this first deposit in the vault which adds liquidity to the AMM, and manually call _addLiquidity in the UniV2 pool which calls->
https://github.com/Uniswap/v2-periphery/blob/master/contracts/UniswapV2Router02.sol#L33
and since the pool is empty the attacker can decide the initial ratio of the pool and disrupt the ratio (can be as extreme as possible) and the amount of subsequent deposits of CT/RA in the AMM would follow this initial ratio.

The attacker can decide the initial ratio of the AMM pool and disrupt subsequent CT/RA deposits in the pool and incorrect DS mints, offload that initialization on the config contract so that only the config contract owner can initialize the vault.

1. Massive Liquidity Drain:
• Initial liquidity: 1,000,000 RA : 100,000 CT
• Loss: ~70% of RA liquidity

2. LP Token Devaluation:
• LP tokens now represent a share of a much smaller pool
• Value per LP token decreased by approximately 70%

Impact translated to LV Holders (other users):
1. Liquidity Liquidation: When DS expires, the allowbreak _liquidatedLp function is called:
• AMM liquidation yields only 300,000 RA (instead of 1,000,000 RA)

2. Reserve Calculation: The reserve function in VaultPool is called with drastically reduced amounts:
• Total LV issued: ~1,000,000 LV (unchanged)
• Available RA: ~300,000 (from AMM)

3. Rate Calculation per LV:
• Before attack: ~1 RA per LV (1,000,000 RA for 1,000,000 LV)
• After attack: ~0.3 RA per LV (300,000 RA for 1,000,000 LV)

4. Impact on Redemptions: When users redeem their LV tokens:
• For every 1,000 LV redeemed, users receive approximately:
– 300 RA (instead of 1,000 RA)
• This represents a 70% loss in value compared to the original deposit

This vulnerability allows an attacker to manipulate the AMM price, forcing the protocol to provide liquidity at an unfavorable rate. The subsequent arbitrage drains significant RA from the AMM pool.

The impact is severe with:
1. Direct value extraction by the attacker
2. Significant devaluation of LV tokens, causing loss for all LV holders.

0xsimao
This is the slippage issue.
0xNirix
issue.
0xsimao
The user is depositing to the vault without control over the amount of ra and ct it will get, which means it is a slippage issue. By placing a slippage check this issue disappears.
Even if you set the initial ratio of the amm, an attacker can always manipulate the price of the pool.

WangSecurity
depositing at this skewed rate (10 RA : 1 CT)?
0xsimao
Yes
WangSecurity
Hmm, but I actually see how the problem here is not just no slippage protection. Even if such a situation happens, and the user deposits 1M Ra and 100k CT with the 10:1 exchange rate, they firstly don't lose anything in value after the deposit, and after withdrawing (before the swap), they don't lose anything. So, it's not about no slippage protection on the deposit cause adding it wouldn't fix anything.

About the POC:
1. The following numbers look arbitrary (i.e. there's no explanation how you've received those numbers so it looks like just randomly picked numbers. I'm sorry if that's not the case, but it's hard to say, since there's no explanation how we received them):
Attacker's arbitrage: Swaps 200,000 CT for 700,000 RA in AMM (price impact 300,000 RA : 300,000 CT)
It may be that the price wouldn't be 300k RA: 300k CT or that the attacker would've got 700k RA.

2. This situation could've been arbitraged easily before anyone deposited into the pool. The attacker deposited 1000 RA and 100 CT, so anyone seeing they can get 10 RA for 1 CT would instantly do that.

3. The depositor can refrain from depositing into the pool if they see an exchange rate like that and wait for the price to stabilise.
Hence, my decision to reject the escalation and leave the issue as it is remains.

0xsimao
It is a slippage issue because the user should not deposit if the exchange rate is so bad (10:1), unless it is frontrunned and the exchange rate gets worse. If a user deposits with an exchange rate 10:1, most of the funds will be arbitraged away. The fix is the user setting slippage so the price stays near the exchange rate.

0xNirix
The following numbers look arbitrary (i.e. there's no explanation how you've received those numbers so it looks like just randomly picked numbers. I'm sorry if that's not the case, but it's hard to say, since there's no explanation how we received them): Attacker's arbitrage: Swaps 200,000 CT for 700,000 RA in AMM 300,000 RA : 300,000 CT It may be that the price wouldn't be 300k RA: 300k CT or that the attacker would've got 700k RA.

Yes, like I mentioned these are approximate but roughly correct numbers but omitted some details for brevity. To arrive at above number I used uniswap v2 swap formula. Here is the breakdown:
1. Initial state:
• RA (Reserve A) = 1,000,000
• CT (Reserve B) = 100,000

2. Constant product (k): k = RA * CT = 1,000,000 * 100,000 = 100,000,000,000

3. The swap: User wants to swap 200,000 CT for RA
4. New CT balance after swap: CT_new = 100,000 + 200,000 = 300,000

5. Calculate new RA balance using the constant product formula: k = RA_new * CT_new 100,000,000,000 = RA_new * 300,000 RA_new = 100,000,000,000 / 300,000 = 333,333.33 (rounded to 2 decimal places)

6. Amount of RA given to the user: RA_out = 1,000,000 - 333,333.33 = 666,666.67

This situation could've been arbitraged easily before anyone deposited into the pool. The attacker deposited 1000 RA and 100 CT, so anyone seeing they can get 10 RA for 1 CT would instantly do that.
Arbitrage is only expected if it would profit the arbitrageurs. The attacker can set the price by using a very small amount e.g. .01 RA and 0.001 CT and we should not expect someone to be able to make any profit off that.

The depositor can refrain from depositing into the pool if they see an exchange rate like that and wait for the price to stabilise.
The protocol deposits to pool automatically when a user deposits to its liquidity vault (LV). For this LV vault, the user is concerned only about the RA to LV token exchange rate. The price of RA to LV is determined by a separate exchange rate which is refreshed periodically at protocol determined expiration time. So user will not know about this liquidity drain impact till the expiration time (which can be anything e.g. after several days). This LV functionality where user is depositing RA, has pool deposits as an internal mechanism.

WangSecurity
It is a slippage issue because the user should not deposit if the exchange rate is so bad (10:1), unless it is frontrunned and the exchange rate gets worse. If a user deposits with an exchange rate 10:1, most of the funds will be arbitraged away. The fix is the user setting slippage so the price stays near the exchange rate

But, the depositor doesn't lose in value just by depositing. Their value before and after the deposit is the same, and they didn't lose anything. Even if there's slippage protection, they deposit without any loss, and a swap to ”drain liquidity” is made after the deposit has occurred, and the slippage check wouldn't catch it.

About the calculations, thank you very much for elaborating, I appreciate it. But the users still get 1 CT + 1 DS for 1 RA and can arbitrage the skewed exchange rate themselves, isn't it correct?

0xsimao
For arbitrage to happen, someone needs to act on this, if no one arbitrages, then value stays drained, and exchange rate, depositing with a bad exchange rate will never go through. Providing liquidity to pools also has slippage checks.

0xNirix
Correct @WangSecurity, anyone can arbitrage the exchange rate back, however that should not be considered as mitigation because:
arbitrage the rate back unless it is to their profit. Arbitrage is only expected if it would profit the arbitrageurs. The attacker can set the price by using a very small amount e.g. .01 RA and 0.001 CT and we should not expect someone to be able to make any profit off that.

2. The users at loss specifically here are LV depositors, they are looking to earn yield on their RA tokens, they should not be expected to know about an internal RA:CT pool that LV internally deposits into as the pool's current rate does not matter to them in anyway during the deposit.

cvetanovv
I think this issue is valid, and escalation can be accepted.
I had originally left this issue valid, and the only reason I invalidated it is that the condition for this to happen is for the pool to be empty.
But @0xNirix showed early in the discussion that the pool will always be empty. We even see:
```solidity
// do nothing at first issuance
if (prevDsId == 0) {
    return;
}
```
Arguments that the admin can prevent this attack are invalid.
A user can front-run his transaction and do the attack before the second function call.
And what would be the logic of developers putting return once they want to call the function again to add liquidity? There is no logic in this, and it confirms that the pool will be empty, and vulnerability is possible.

Also, the arguments that it is a duplicate of the slippage group are invalid. You can see the duplication rules:
Even if the root-cause is the same, the attack path is different: Only when the "potential duplicate" meets all four requirements will the "potential duplicate" be duplicated with the "target issue"

WangSecurity
I agree with @cvetanovv, and I believe he explained very well why this issue has to be valid. Planning to accept the escalation and validate the family with medium severity.
Plan to apply this decision in a couple of hours.

0xsimao

WangSecurity
As I've said a couple of times earlier, this is not a slippage-related issue, and I stand by my previous arguments about this. The decision remains as in my previous message: accept the escalation and validate with medium severity. Planning to apply this decision in a couple of hours.

0xsimao
The issue only happens because someone frontruns the user and sets a different exchange rate. If the user deposits with a bad exchange rate, it's their fault.
It's exactly like providing liquidity to a uniswap pool, users also set minimum amounts A and B, so they can control the ratio.
If slippage is added then users always deposit with a favorable exchange rate and this is resolved.
Front-running/sandwich/slippage protection:

WangSecurity
The issue only happens because someone frontruns the user and sets a different exchange rate
Front-running is not required here.
If the user deposits with a bad exchange rate, it's their fault.
It's exactly like providing liquidity to a uniswap pool, users also set minimum amounts A and B, so they can control the ratio. If slippage is added then users always deposit with a favorable exchange rate and this is resolved.
slippage is mentioned directly in the rules for groups and the issue can be resolved.

What matters here is the RA to LV exchange rate, and it would be correct. So if we implement slippage protection for this, it won't fix the issue.

Moreover, even if considered a slippage-related issue, this family deserves to be separated based on the following:
The exception to this would be if underlying code implementations OR impact OR the fixes are different, then they may be treated separately.

The decision remains, accept the escalation and validate with medium severity, the decision will be applied tomorrow 10 AM UTC.

0xsimao
will arbitrage the rate back unless it is to their profit. Arbitrage is only expected if it would profit the arbitrageurs. The attacker can set the price by using a very small amount e.g. .01 RA and 0.001 CT and we should not expect someone to be able to make any profit off that.
It is for their profit, they will do it.
The users at loss specifically here are LV depositors, they are looking to earn yield on their RA tokens, they should not be expected to know about an internal RA:CT pool that LV internally deposits into as the pool's current rate does not matter to them in anyway during the deposit.

Again, it was their choice to deposit with a bad exchange rate. Unless they are frontrunned. Obviously users do not deposit blindly, they should set an exchange rate limit, but they do not, as it is a slippage issue. This is like saying depositing in a uniswap pool should not have slippage control, which makes no sense.

What matters here is the RA to LV exchange rate, and it would be correct. So if we implement slippage protection for this, it won't fix the issue.
It fixes it because users would never deposit with a bad exchange rate, it would be a mistake.

The exception to this would be if underlying code implementations OR impact OR the fixes are different, then they may be treated separately.
But everything is the same, slippage when interacting with a uniswap pool. The bug is here:
```solidity
(,, uint256 lp) = ammRouter.addLiquidity(
    token0, token1, token0Amount, token1Amount, token0Tolerance, token1Tolerance,
    address(this), block.timestamp
);
```
The tolerances are incorrectly calculated on chain, they should be passed as arguments.

WangSecurity
Again, it was their choice to deposit with a bad exchange rate. Unless they are frontrunned. Obviously users do not deposit blindly, they should set an exchange rate limit, but they do not, as it is a slippage issue. This is like saying depositing in a uniswap pool should not have slippage control, which makes no sense

The exchange rate remains before and after the deposit. Even if you set an exchange rate limit it doesn't matter here because it doesn't change and that slippage check would be satisfied.

It fixes it because users would never deposit with a bad exchange rate, it would be a mistake
The RA:LV exchange would be correct, and it wouldn't be a mistake to deposit at the correct RA:LV exchange rate. The problem is in the RA:CT exchange rate and setting slippage protection to RA:LV exchange rate doesn't fix the problem of the RA:CT exchange rate.

My decision to accept the escalation and validate with medium severity remains and it's final.

WangSecurity
Result: Medium Has duplicates
Escalations have been resolved successfully!
Escalation status:
• cvetanovv: rejected

## Recommendation
offload that initialization on the config contract so that only the config contract owner can initialize the vault.
