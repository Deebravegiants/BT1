# [M] Possible Reentrency not-involving-eth Issues [RCOrderbook.sol]

## Summary
Severity: Medium
Chain: Smart contract
Component: 2021-06-realitycards
Published: 2021-06-15
Source: https://github.com/code-423n4/2021-06-realitycards-findings/issues/47
Type: code-finding

## Details
# Handle

maplesyrup


# Vulnerability details

## Impact

2 - Medium Risk
   - Possible reentrancy found in the contract, possible loss of funds due to code manipulation

## Proof of Concept

According to the Slither-analyzer documentation (https://github.com/crytic/slither/wiki/Detector-Documentation#configuration-32): Detection of reentrancy was found in the following functions as there are external calls made before state variables are changed. This can lead to a possible attack on the functions and contract.

Reentrancy found in:

contracts/RCOrderbook.sol

line(s) 280-340

RCOrderbook._newBidInOrderbook(address, address, uint256, uint256, uint256, RCOrderbook.Bid) 

External calls:

	treasury.increaseBidRate(_user,_price) 
	(contracts/RCOrderbook.sol line(s)#328)
	
	transferCard(_market,_card,_oldOwner,_user,_price) 
	(contracts/RCOrderbook.sol line(s)#331)
	
	_rcmarket.transferCard(_oldOwner,_newOwner,_card,_price,_timeLimit) 
	(contracts/RCOrderbook.sol line(s)#870)


State variables written after the call(s):


_Trimmed to 38 lines — full report: https://github.com/code-423n4/2021-06-realitycards-findings/issues/47_
