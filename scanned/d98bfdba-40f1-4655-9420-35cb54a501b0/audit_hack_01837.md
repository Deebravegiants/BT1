# [H] Rounding errors after slashing

## Summary
Severity: High
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
#### Description

When slashing happens `_delegatedToValidator` and `_effectiveDelegatedToValidator` values are reduced.
 

**new_code/contracts/delegation/DelegationController.sol:L349-L355**
```solidity
function confiscate(uint validatorId, uint amount) external {
    uint currentMonth = getCurrentMonth();
    Fraction memory coefficient = reduce(_delegatedToValidator[validatorId], amount, currentMonth);
    reduce(_effectiveDelegatedToValidator[validatorId], coefficient, currentMonth);
    putToSlashingLog(_slashesOfValidator[validatorId], coefficient, currentMonth);
    _slashes.push(SlashingEvent({reducingCoefficient: coefficient, validatorId: validatorId, month: currentMonth}));
}
```

When holders process slashings, they reduce `_delegatedByHolderToValidator`, `_delegatedByHolder`, `_effectiveDelegatedByHolderToValidator` values. 


**new_code/contracts/delegation/DelegationController.sol:L892-L904**
```solidity
if (oldValue > 0) {
    reduce(
        _delegatedByHolderToValidator[holder][validatorId],
        _delegatedByHolder[holder],
        _slashes[index].reducingCoefficient,
        month);
    reduce(
        _effectiveDelegatedByHolderToValidator[holder][validatorId],
        _slashes[index].reducingCoefficient,
        month);
    slashingSignals[index.sub(begin)].holder = holder;
    slashingSignals[index.sub(begin)].penalty = oldValue.sub(getAndUpdateDelegatedByHolderToValidator(holder, validatorId, month));
}
```

Also when holders are undelegating, they are calculating how many tokens from `delegations[delegationId].amount` were slashed.


**new_code/contracts/delegation/DelegationController.sol:L316**
```solidity
uint amountAfterSlashing = calculateDelegationAmountAfterSlashing(delegationId);
```

All these values should be calculated one from another, but they all will have different rounding errors after slashing. For example, the assumptions that the total sum of all delegations from holder `X` to validator `Y` should still be equal to `_delegatedByHolderToValidator[X][Y]` is not true anymore. The problem is that these assumptions are still used. For example, when undelegating some delegation with delegated amount equals `amount`(after slashing), the holder will reduce `_delegatedByHolderToValidator[X][Y]`,  `_delegatedByHolder[X]` and `_delegatedToValidator[Y]` by `amount`. Since rounding errors of all these values are different that will lead to 2 possible scenarios:

1. If rounding error reduces `amount` not that much as other values, we can have `uint` underflow. This is especially dangerous because all calculations are delayed and we will know about underflow and `SafeMath` revert in the next month or later.  
_Developers already made sure that rounding errors are aligned in a correct way, and that the reduced value should always be larger than the subtracted, so there should not be underflow. This solution is very unstable because it's hard to verify it and keep in mind even during a small code change._

2. If rounding errors make `amount` smaller then it should be, when other values should be zero (for example, when all the delegations are undelegated), these values will become some very small values. The problem here is that it would be impossible to compare values to zero.


#### Recommendation

1. Consider not calling `revert` on these subtractions and make result value be equals to zero if underflow happens.
2. Consider comparing to some small `epsilon` value instead of zero. Or similar to the previous point, on every subtraction check if the value is smaller then `epsilon`, and make it zero if it is.
