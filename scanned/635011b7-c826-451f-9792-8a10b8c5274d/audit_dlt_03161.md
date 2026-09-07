# [M] Uninitialized Local Variables found in RCOrderbook.sol

## Summary
Severity: Medium
Chain: Smart contract
Component: 2021-06-realitycards
Published: 2021-06-15
Source: https://github.com/code-423n4/2021-06-realitycards-findings/issues/50
Type: code-finding

## Details
# Handle

maplesyrup


# Vulnerability details

## Impact

2 - Medium Risk
   - Possible accidental loss of funds if variables do not contain the right information such as correct addresses in this specific scenario.

## Proof of Concept
According to Slither documentation (https://github.com/crytic/slither/wiki/Detector-Documentation#configuration-32), uninitialized local variables can cause the risk of loss of funds due to inappropriate usage of these variables while using the contract. All variables must be initialized to insure they do not run the risk of incorrect calculations or sending funds to a 0x0 address.

It is recommended that all variables need to be initialized. If the variable needs to be 0, then it is best to explicitly assign 0 to the variable.

The following local variables in RCOrderbook are not initialized:

RCOrderbook.getBid(address,address,uint256)._newBid <--- is a local variable never initialized

(contracts/RCOrderbook.sol line(s)#818)

 -------------------------------------------------------------------

RCOrderbook.removeOldBids(address)._cardCount <--- is a local variable never initialized

(contracts/RCOrderbook.sol line(s)#676)

 -------------------------------------------------------------------

RCOrderbook._newBidInOrderbook(address,address,uint256,uint256,uint256,RCOrderbook.Bid)._newBid <--- is a local variable never initialized

(contracts/RCOrderbook.sol line(s)#301)

 -------------------------------------------------------------------

RCOrderbook.addMarket(address,uint256,uint256).i <--- is a local variable never initialized

_Trimmed to 38 lines — full report: https://github.com/code-423n4/2021-06-realitycards-findings/issues/50_
