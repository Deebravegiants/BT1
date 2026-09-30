# [M] theft of system profit

## Summary
Severity: Medium
Contest weight: 0.2686
Dataset id: 1143
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
System profit comes from the stabilize function when the price of malt is above 1. Therefore it should not be allowed for anyone to take a part of the system profit when the price is above one. Right now, anyone can take a part of the investors’ profits, even if they don’t own any malt at all.

## Proof of Concept
suppose that the price went up to 1.2 dai; the investors should get the reward for this rise. instead, anyone can take a part of the reward in the following steps: The price of malt is now 1.2 dai. Take a flash loan of a large amount of malt. Sell the malt for dai. Now the price went down to 1.1 dai because of the enormous swap. Call stabilize in order to lower the price to 1 dai. Buy malt to repay the flash loan at a lower cost with the bought dai. Repay the flash loan, and take the profit.

It is a sandwich attack because they sold malt for a high price, then they called stabilize to lower the value, then repurchase it for a low price.

The user made a profit at the expense of the investors.

If a user already has malt, it’s even easier: just sell all malt at a high cost.

## Recommendation
in _beforeTokenTransfer, if the price is above 1$ and the receiver is the AMM pool, stabilize it.

@0xScotch The warden says that if the price is above the peg price, the system should stabilize it From reading the `PoolTransferVerification.verifyTransfer`, the system wants you to trade when Malt is above peg (minus tolerance)

Would you say this finding is invalid?

> @0xScotch The warden says that if the price is above the peg price, the system should stabilize it From reading the `PoolTransferVerification.verifyTransfer`, the system wants you to trade when Malt is above peg (minus tolerance)
>> 
>> Would you say this finding is invalid?
> 
> I think the issue being pointed out is that the stabilization above peg can be sandwiched and some profit that would go to LPs can be extracted. I think this is an issue but its not absolutely critical.
> 
> We have discussed internally how to deal with this and the suggestion of calling stabilize would require some additional logic in the transfer verification as it would create a circular execution path.
> 
>   1. User tries to sell at 1.2
>   2. Transfer verifier triggers stabilize
>   3. StabilizerNode tries to sell Malt ahead of initial user
>   4. Transfer verifier runs again and will call stabilize again unless we modify it to deal with this case.
> 
> I don’t think that is an issue but we will consider how to best move ahead with it.

Let’s dissect the warden’s finding:
    
    The price of malt is now 1.2 dai.
    Take a flash loan of a large amount of malt.
    Sell the malt for dai.
    Now the price went down to 1.1 dai because of the enormous swap.
    Call stabilize in order to lower the price to 1 dai.
    Buy malt to repay the flash loan at a lower cost with the bought dai.
    Repay the flash loan, and take the profit.

-> Flashloan Malt (assumes liquidity to do so, but let’s allow that) -> Sell malt for dai -> price goes lower -> Call stabilize -> system reduces price even further -> Buy back the malt -> repay the loan

I feel like this is something that can’t really be avoided as due to the permissionless nature of liquidity pools, limiting the ability to sell or buy to a path will be sidestepped by having other pools being deployed to avoid those checks.

That said, the warden has identified a way to leak value from the price control system.

To be precise the value is being extracted against traders, as to get Malt to 1.2 you’d need a trader to be so aggressive in their purchase to push the price that high. The warden showed how any arber / frontrunner can then “steal” the potential profits of the malt system users by frontrunning them.

Due to the profit extraction nature of the finding, I believe Medium Severity to be correct
