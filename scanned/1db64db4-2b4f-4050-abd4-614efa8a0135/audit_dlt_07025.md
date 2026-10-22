# [M] can't trigger the vote function

## Summary
Severity: Medium
Chain: Smart contract
Component: 2024-09-fenix-finance
Published: 2024-09-25
Source: https://github.com/code-423n4/2024-09-fenix-finance-findings/issues/21
Type: code-finding

## Details
# Lines of code

https://github.com/code-423n4/2024-09-fenix-finance/blob/main/contracts/core/VoterUpgradeableV2.sol#L485
https://github.com/code-423n4/2024-09-fenix-finance/blob/main/contracts/core/VoterUpgradeableV2.sol#L448


# Vulnerability details

## Description

The `VoterUpgradeableV2.sol` contract has the function `attachToManagedNFT()`, users use it to delegate their veFNX voting power to a mVeNFT.
One of the things this function does after receiving the new voting power is sub-call to `_poke()` and it will update the Last voted Timestamp of the mVeNFT 
```solidity
lastVotedTimestamps[tokenId_] = _epochTimestamp() + 1;
```
At this point, the mVeNFT can't trigger the vote function until the next epoch starts due to the `_checkVoteDelay()`.
even this check inside the `vote()` doesn't help in this case 
```solidity
if (!managedNFTManagerCache.isWhitelistedNFT(tokenId_)) {
            _checkEndVoteWindow();
        }
```
  
However, to make things worse this protocol is deployed on Blast transactions are too cheap 
malicious users can keep creating new locks every epoch with one wei in `amount`  to bypass the zero check
```solidity
File: VotingEscrowUpgradeableV2.sol#_createLock()

 LibVotingEscrowValidation.checkNoValueZero(amount_);
```
then at the start of every new epoch (after the start of the voting window) just call `attachToManagedNFT()` 
By doing this it keeps forcing the mVeNFT to vote to the same gauges.


## Impact
DOS attack. 
mVeNFT can't invoke the vote function to change the weight of gauges. 
mVeNFT can't reset its votes.

## Tools Used

Manual Review

## Recommended Mitigation Steps
One solution is to not check the vote delay, However, I believe this comes with some trade-off
```solidity
    function vote(
        uint256 tokenId_,
        address[] calldata poolsVotes_,
        uint256[] calldata weights_
    ) external nonReentrant onlyNftApprovedOrOwner(tokenId_) {
        if (poolsVotes_.length != weights_.length) {
            revert ArrayLengthMismatch();
        }
        bool x = managedNFTManagerCache.isWhitelistedNFT(tokenId_);
        if (!x) {
        _checkVoteDelay(tokenId_);
        }

        _checkStartVoteWindow();
        IManagedNFTManager managedNFTManagerCache = IManagedNFTManager(managedNFTManager);
        if (managedNFTManagerCache.isDisabledNFT(tokenId_)) {
            revert DisabledManagedNft();
        }
        if (!x) {
            _checkEndVoteWindow();
        }
        _vote(tokenId_, poolsVotes_, weights_);
        _updateLastVotedTimestamp(tokenId_);
    }
```


## Assessed type

DoS
