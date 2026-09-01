# [M] withdrawFees does not update checkpoint

## Summary
Severity: Medium
Chain: Smart contract
Component: 2023-08-livepeer
Published: 2023-09-05
Source: https://github.com/code-423n4/2023-08-livepeer-findings/issues/104
Type: code-finding

## Details
# Lines of code

https://github.com/code-423n4/2023-08-livepeer/blob/bcf493b98d0ef835e969e637f25ea51ab77fabb6/contracts/bonding/BondingManager.sol#L273-L277
https://github.com/code-423n4/2023-08-livepeer/blob/bcf493b98d0ef835e969e637f25ea51ab77fabb6/contracts/bonding/BondingManager.sol#L130-L133
https://github.com/code-423n4/2023-08-livepeer/blob/bcf493b98d0ef835e969e637f25ea51ab77fabb6/contracts/bonding/BondingManager.sol#L1667-L1671
https://github.com/code-423n4/2023-08-livepeer/blob/bcf493b98d0ef835e969e637f25ea51ab77fabb6/contracts/bonding/BondingManager.sol#L1500-L1552


# Vulnerability details

## Impact
BondingVotes may have stale data due to missing checkpoint in BondingManager#withdrawFees().

## Proof of Concept
The withdrawFee function has the autoClaimEarnings modifier:
```Solidity
    function withdrawFees(address payable _recipient, uint256 _amount) external whenSystemNotPaused currentRoundInitialized autoClaimEarnings(msg.sender) {
```
which calls _autoClaimEarnings:
```Solidity
modifier autoClaimEarnings(address _delegator) {
        _autoClaimEarnings(_delegator);
        _;
```

which calls updateDelegatorWithEarnings:
```Solidity
function _autoClaimEarnings(address _delegator) internal {
        uint256 currentRound = roundsManager().currentRound();
        uint256 lastClaimRound = delegators[_delegator].lastClaimRound;
        if (lastClaimRound < currentRound) {
            updateDelegatorWithEarnings(_delegator, currentRound, lastClaimRound);
        }
    }
```
During updateDelegatorWithEarnings both delegator.lastClaimRound delegator.bondedAmount can be assigned new values.
```Solidity
        del.lastClaimRound = _endRound;
```

_Trimmed to 38 lines — full report: https://github.com/code-423n4/2023-08-livepeer-findings/issues/104_
