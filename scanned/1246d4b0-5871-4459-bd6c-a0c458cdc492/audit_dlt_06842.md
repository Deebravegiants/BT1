# [M] Parameter updates not propagated

## Summary
Severity: Medium
Chain: Smart contract
Component: 2021-08-realitycards
Published: 2021-08-22
Source: https://github.com/code-423n4/2021-08-realitycards-findings/issues/30
Type: code-finding

## Details
# Handle

gpersoon


# Vulnerability details

## Impact
There are several functions to update parameters. However these parameters are only updated on the top level and not propagated to the other contracts. This could lead to various unpredictable results.
Examples are:
- setNftHubAddress of RCFactory
- setOrderbookAddress of RCFactory
- setLeaderboardAddress of RCFactory
- setMinRental of RCTreasury

## Proof of Concept
// https://github.com/code-423n4/2021-08-realitycards/blob/main/contracts/RCFactory.sol#L586
 function setNftHubAddress(IRCNftHubL2 _newAddress) external override onlyUberOwner {
        require(address(_newAddress) != address(0), "Must set Address");
        nfthub = _newAddress;
    }

    function setOrderbookAddress(IRCOrderbook _newOrderbook) external override {
        require( treasury.checkPermission(TREASURY, msgSender()), "Not approved" );
        orderbook = _newOrderbook;
    }

 function setLeaderboardAddress(IRCLeaderboard _newLeaderboard) external override {
        require( treasury.checkPermission(TREASURY, msgSender()), "Not approved");
        leaderboard = _newLeaderboard;
    }

//https://github.com/code-423n4/2021-08-realitycards/blob/main/contracts/RCTreasury.sol#L188
 function setMinRental(uint256 _newDivisor) public override onlyRole(OWNER) {
        minRentalDayDivisor = _newDivisor;
    }

## Tools Used

_Trimmed to 38 lines — full report: https://github.com/code-423n4/2021-08-realitycards-findings/issues/30_
