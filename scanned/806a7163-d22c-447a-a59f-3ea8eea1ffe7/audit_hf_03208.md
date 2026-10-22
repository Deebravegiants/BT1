# [H] The total community voting power is updated

## Summary
Severity: High
Contest weight: 0.7609
Dataset id: 17794
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
When a user delegates their voting power from staked tokens, the total community voting power should be updated. But the update logic is not correct, the total community voting power could be wrong values.
```solidity
tokenVotingPower[currentDelegate] -= amount;
tokenVotingPower[_delegatee] += amount;
// If a user is delegating back to themselves, they regain their community voting power, so adjust totals up
if (_delegator == _delegatee) {
    _updateTotalCommunityVotingPower(_delegator, true);
// If a user delegates away their votes, they forfeit their community voting power, so adjust totals down
} else if (currentDelegate == _delegator) {
    _updateTotalCommunityVotingPower(_delegator, false);
}
```
When the total community voting power is increased in the first if statement, _delegator's token voting power might be positive already and community voting power might be added to total community voting power before. Also, currentDelegate's token voting power might be still positive after delegation so we shouldn't remove the community voting power this time. The total community voting power can be incorrect.

## Recommendation
Add more conditions to check if the msg.sender delegated or not.
```solidity
if (_delegator == _delegatee) {
    if(tokenVotingPower[_delegatee] == amount) {
        _updateTotalCommunityVotingPower(_delegator, true);
    }
    if(tokenVotingPower[currentDelegate] == 0) {
        _updateTotalCommunityVotingPower(currentDelegate, false);
    }
} else if (currentDelegate == _delegator) {
    if(tokenVotingPower[_delegatee] == amount) {
        _updateTotalCommunityVotingPower(_delegatee, true);
    }
    if(tokenVotingPower[_delegator] == 0) {
        _updateTotalCommunityVotingPower(_delegator, false);
    }
}
```
