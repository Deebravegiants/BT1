# [M] MeritDutchAuction::claimProceeds emit incorrect event

## Summary
Severity: Medium
Reporter: ww4tson
Source: https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritDutchAuction.sol#L178
Type: audit-issue

## Details
# MeritDutchAuction::claimProceeds emit incorrect event

## Summary
MeritDutchAuction::claimProceeds emit incorrect event which has zero for balance.

## Vulnerability Detail
```solidity
    function claimProceeds() external onlyOwner {
        (bool success, ) = payable(msg.sender).call{value: address(this).balance}(bytes(""));
        require(success, "Claim failed");
        emit ClaimedProceeds(address(this).balance);
    }
```
Since the funds have been already transferred, `address(this).balance` in the `ClaimedProceeds` will be always 0.

## Impact
If the event is used off-chain for important operations, it will cause damage to protocol.

## Code Snippet
https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritDutchAuction.sol#L178

## Tool used

Manual Review

## Recommendation
Cache `address(this).balance` in a local var and use it.
