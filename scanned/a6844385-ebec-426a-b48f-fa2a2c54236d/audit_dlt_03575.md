# [M] dutchTradeDisabled[erc20] gives governance an incentive to disable RSR auctions

## Summary
Severity: Medium
Chain: Smart contract
Component: 2023-08-reserve-mitigation
Published: 2023-08-18
Source: https://github.com/code-423n4/2023-08-reserve-mitigation-findings/issues/20
Type: code-finding

## Details
# Lines of code

https://github.com/reserve-protocol/protocol/blob/3.0.0-rc5/contracts/p1/Broker.sol#L213-L216


# Vulnerability details

The mitigation adds different disable flags for GnosisTrade and DutchTrade. It can disable dutch trades by specific collateral. But it has serious problem with overall economic model design. 

The traders Broker contract are under control of the governance. The governance proposals are voted by stRSR stakers. And if the RToken is undercollateralized, the staking RSR will be sold for collaterals. In order to prevent this from happening, the governance(stakers) have every incentive to block the rsr auction. Although governance also can set disable flag for trade broker in the previous version of mitigation, there is a difference made it impossible to do so in previous versions. 

In the pre version, there is only one disable flag that disables any trades for any token. So if the governance votes for disable trades, the RToken users will find that they can't derive any gain from RToken. So no one would try to issue RToken by their collateral. It is also unacceptable for governance.

But after the mitigation, the governance can decide only disable the DutchTrade for RSR. And they can initiate a proposal about enable RSR trade -> open openTrade -> re-disable RSR trade to ensure their own gains. And most importantly, this behavior seems to do no harm to RToken holders just on the face of it, and it therefore does not threaten RToken issuance.

So in order to prevent the undercollateralized case, dutchTradeDisabled[erc20] gives governance every incentive to disable RSR auctions.

## Impact
When RToken is undercollateralized, disabling RSR trade will force users into redeeming from RToken baskets. It will lead to even greater depeg, and the RToken users will bear all the losses, but the RSR stakers can emerge unscathed.

## Proof of Concept
StRSR stakers can initiate such a proposal to prevent staking RSR auctions:

1. Call `Broker.setBatchTradeDisabled(bool disabled)` to disable any GnosisTrade.

2. And call `setDutchTradeDisabled(RSR_address, true)` to disable RSR DutchTrade.

## Tools Used
Manual review

## Recommended Mitigation Steps
The `dutchTradeDisabled` flag of RSR should not be set to true directly by governance in the `Broker.setDutchTradeDisabled` function. Add a check like that:
```
require(!(disabled && rsrTrader.tokenToBuy()==erc20),"xxxxxxx");
```


## Assessed type

_Trimmed to 38 lines — full report: https://github.com/code-423n4/2023-08-reserve-mitigation-findings/issues/20_
