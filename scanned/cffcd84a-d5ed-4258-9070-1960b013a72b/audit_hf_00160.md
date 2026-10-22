# [M] Parameter updates not propagated

## Summary
Severity: Medium
Contest weight: 0.4543
Dataset id: 842
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
There are several functions to update parameters. However these parameters are only updated on the top level and not propagated to the other contracts. This could lead to various unpredictable results. Examples are:

  * `setNftHubAddress` of `RCFactory`
  * `setOrderbookAddress` of `RCFactory`
  * `setLeaderboardAddress` of `RCFactory`
  * `setMinRental` of `RCTreasury`

```solidity
function setNftHubAddress(IRCNftHubL2 _newAddress) external override onlyUberOwner {
    require(address(_newAddress) != address(0), "Must set Address");
    nfthub = _newAddress;
}

function setOrderbookAddress(IRCOrderbook _newOrderbook) external override {
    require(treasury.checkPermission(TREASURY, msgSender()), "Not approved");
    orderbook = _newOrderbook;
}

function setLeaderboardAddress(IRCLeaderboard _newLeaderboard) external override {
    require(treasury.checkPermission(TREASURY, msgSender()), "Not approved");
    leaderboard = _newLeaderboard;
}

function setMinRental(uint256 _newDivisor) public override onlyRole(OWNER) {
    minRentalDayDivisor = _newDivisor;
}
```

Recommend implementing a way to notify the underlying contracts of the updates.

We have come to realise that it is very unlikely we will be able to change certain contracts once they are in-use, the exception being the market where a new reference could be deployed. In practice we do use `setNftHubAddress` shortly after deploying new contracts, this is so that we can continue to use an existing NFT hub that has already been put through Matic Mintable Asset mapping, but changing this while a market is active would cause problems. While we accept that changing these parameters on active contracts may be troublesome we will not be making changes at this time, partly because it’s useful to be able to change these before the contracts are in use but also due to the potential risk of introducing new problems at this stage in the project.

## Recommendation
No recommendation
