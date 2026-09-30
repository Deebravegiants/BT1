# [M] avoid paying insurance

## Summary
Severity: Medium
Contest weight: 0.2427
Dataset id: 604
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
It’s possible to avoid paying insurance in the following way:

* once per hour (at the right moment), do the following:
* using a flash loan, or with a large amount of tokens, call `deposit` of `Insurance.sol` to make sure that the pool is sufficiently filled (`poolHoldings` > `poolTarget`)
* call the function `executeTrade` of Trader.sol with a minimal trade (possibly of value 0, see finding ”`executeTrade` with same trades”)
* `executeTrade` calls `matchOrders`, which calls `recordTrade`
* `recordTrade` calls `updateFundingRate()`; (once per hour, so you have to be sure you do it in time before other trades trigger this)
* `updateFundingRate` calls `getPoolFundingRate`
* `getPoolFundingRate` determines the insurance rate, but because the insurance pool is sufficiently full (due to the flash loan), the rate is 0
* `updateFundingRate` stores the 0 rate via `setInsuranceFundingRate` (which is used later on to calculate the amounts for the insurances)
* withdraw from the Insurance and pay back the flash loan

The insurance rates are 0 now and no-one pays insurance. The gas costs relative to the insurance costs + the flash loan fees determine if this is an economically viable attack. Otherwise it is still a grief attack. This will probably be detected pretty soon because the insurance pool will stay empty. However its difficult to prevent.

See issue page for code referenced in proof of concept.

Recommend setting a timelock on withdrawing insurance.

Really like this exploit idea. Currently this is possible since the Trader is not whitelisted (eg there is no whitelisted relayer address). With this added, this exploit is no longer possible as only off chain relayers can place orders with the trader.

Disagree with the severity mainly due to the fact that executing this exploit once would only cause insurance funding to not be paid for a single hour. For insurance funding to never be paid, you would have to time this transaction as the first transaction on each and every hour. This would quickly be noticed. The only affect on this would be insurance depositors miss interest payments for a few periods.

Marking this as medium risk as a front-runner could keep doing this for not paying any funding using a bot.

## Recommendation
No recommendation
