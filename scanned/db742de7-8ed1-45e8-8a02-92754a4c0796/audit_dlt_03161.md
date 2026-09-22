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

(contracts/RCOrderbook.sol line(s)#166)

 -------------------------------------------------------------------

RCOrderbook.removeOldBids(address)._loopCounter <--- is a local variable never initialized

(contracts/RCOrderbook.sol line(s)#677)

 -------------------------------------------------------------------

RCOrderbook.cleanWastePile().i <--- is a local variable never initialized

(contracts/RCOrderbook.sol line(s)#717)

 -------------------------------------------------------------------

RCOrderbook.closeMarket()._newBid <--- is a local variable never initialized

(contracts/RCOrderbook.sol line(s)#660) 

 -------------------------------------------------------------------

RCOrderbook.addMarket(address,uint256,uint256)._newBid <--- is a local variable never initialized

(contracts/RCOrderbook.sol line(s)#168)

 -------------------------------------------------------------------

Console output (Slither log):

INFO:Detectors:
RCOrderbook.removeOldBids(address)._loopCounter (contracts/RCOrderbook.sol#677) is a local variable never initialized
RCMarket.lockMarket().i (contracts/RCMarket.sol#453) is a local variable never initialized
RCOrderbook.cleanWastePile().i (contracts/RCOrderbook.sol#717) is a local variable never initialized
RCOrderbook.getBid(address,address,uint256)._newBid (contracts/RCOrderbook.sol#818) is a local variable never initialized
RCOrderbook.addMarket(address,uint256,uint256)._newBid (contracts/RCOrderbook.sol#168) is a local variable never initialized
RCOrderbook.addMarket(address,uint256,uint256).i (contracts/RCOrderbook.sol#166) is a local variable never initialized
RCNftHubL2.deposit(address,bytes).i (contracts/nfthubs/RCNftHubL2.sol#150) is a local variable never initialized
RCOrderbook._newBidInOrderbook(address,address,uint256,uint256,uint256,RCOrderbook.Bid)._newBid (contracts/RCOrderbook.sol#301) is a local variable never initialized
RCOrderbook.removeOldBids(address)._cardCount (contracts/RCOrderbook.sol#676) is a local variable never initialized
RCOrderbook.closeMarket()._newBid (contracts/RCOrderbook.sol#660) is a local variable never initialized
Reference: https://github.com/crytic/slither/wiki/Detector-Documentation#uninitialized-local-variables

## Tools Used

Solidity Compiler 0.8.4
Hardhat v2.3.3
Slither v0.8.0

Compiled, Tested, and Deployed contracts on a local Hardhat network

Ran Slither-analyzer for further detecting and testing.

## Recommended Mitigation Steps
(Worked best under a python virtual environment)
1. Clone project repository
3. Run project against hardhat network; 
    compile and run default test on contracts.
4. Installed sliither analyzer:
    https://github.com/crytic/slither
5. Ran [$ slither .] against all contracts
