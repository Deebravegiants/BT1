# [H] 7.2 Collecting Keeper Fees, Closing Perpetuals

## Summary
Severity: High
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
Security High Version 1 Code Corrected

Should the maximum covered amount of collateral be exceeded, anyone can forcefully cash out any
perpetual in order to bring the amount of covered collateral back below the limit. However this can be
abused as one can manipulate the amount of collateral to be covered.

Assume a working StableMaster issuing AgUSD with several collateral pools like USDC, DAI and WETH.
There is a decent amount of liquidity provided by standard liquidity providers and the coverage ratio of
the pools is around 80% with a limit at 90%. Many perpetuals of different sizes exist. An arbitrary attacker
can now do the following:

```
1.Either the Attacker has funds available or borrows them using a flashloan
2.These funds are exchanged into AgUSD on a third party exchange
3.These AgUSD are now burned for the collateral under attack.
```
```
4.Burning the AgUSD tokens increases the collateralization ratio for this collateral as collateral is
withdrawn. The attacker does this at least until the coverage limit is exceeded.
5.The attacker is now able to forcefully cash out perpetuals until the amount covered is below the limit.
While forcefully cashing out perpetuals the attacker collects the fees.
6.Pay back the flashloan using the collateral.
```
This attack is profitable when the transaction, flashloan and burn fees are below the keeper reward
collected for closed perpetuals. As keeper fees for each perpetual have to cover for the transaction base
fees (as they may have to be closed individually by keepers due to reaching the cashout leverage) the
collected rewards likely exceed the fees when the attacker manages to forcefully cash out multiple
perpetuals during this action.

Code corrected:

The new fee structure rewards keepers reaching the targeted coverage ratio. Moreover, the keeper
reward is capped such that the profit of the keeper is lower than the estimated cost of the flash loan
needed for such an attack. For more information see the description of System Accounting.
