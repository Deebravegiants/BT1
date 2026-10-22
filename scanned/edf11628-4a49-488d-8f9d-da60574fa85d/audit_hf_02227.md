# [M] Proper Migration in CorePool::moveFundsFromWallet()

## Summary
Severity: Medium
Contest weight: 0.4597
Dataset id: 12298
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The staking contracts support a neat feature in allowing users to transfer their total positions to new addresses. This is useful in situations such as when a personal private key is leaked or anything that could motivate a user to move into a new address. While analyzing the migration logic, we notice the current implementation needs to be improved. In particular, we show below the related moveFundsFromWallet() function that is tasked to support the migration. While the current implementation properly validates the migration conditions and transfer associated rewards, we notice the logic simply removes the stakes from the migrating user (line 582). In other words, the previous stakes that also need to migrated are simply removed!
```solidity
function moveFundsFromWallet(address _to) public virtual {
    // checks if the contract is in a paused state
    _requireNotPaused();
    // gets storage pointer to msg.sender user struct
    User storage previousUser = users[msg.sender];
    // gets storage pointer desired address user struct
    User storage newUser = users[_to];
    // uses v1 weight values for rewards calculations
    uint256 v1WeightToAdd = _useV1Weight(msg.sender);
    // We process update global and user's rewards
    // before moving the user funds to a new wallet.
    // This way we can ensure that all v1 ids weight have been used before the v2
    // stakes to a new address.
    _updateReward(msg.sender, v1WeightToAdd);
    // we're using selector simplify input and state validation
    bytes4 fnSelector = this.moveFundsFromWallet.selector;
    // validate input is set
    fnSelector.verifyNonZeroInput(uint160(_to), 0);
    // verify new user records are empty
    fnSelector.verifyState(
        newUser.totalWeight == 0 &&
        newUser.v1IdsLength == 0 &&
        newUser.stakes.length == 0 &&
        newUser.yieldRewardsPerWeightPaid == 0 &&
        newUser.vaultRewardsPerWeightPaid == 0,
        0
    );
    // saves previous user total weight
    uint248 previousTotalWeight = previousUser.totalWeight;
    // saves previous user pending yield
    uint128 previousYield = previousUser.pendingYield;
    // saves previous user pending rev dis
    uint128 previousRevDis = previousUser.pendingRevDis;
    // It's expected to have all previous user values migrated to the new user address (_to).
    // We recalculate yield and vault rewards values
    // to make sure new user pending yield and pending rev dis to be stored
    // at newUser.pendingYield and newUser.pendingRevDis is 0, since we just processed
    // all pending rewards calling _updateReward.
    newUser.totalWeight = previousTotalWeight;
    newUser.pendingYield = previousYield;
    newUser.pendingRevDis = previousRevDis;
    newUser.yieldRewardsPerWeightPaid = yieldRewardsPerWeight;
    newUser.vaultRewardsPerWeightPaid = vaultRewardsPerWeight;
    delete previousUser.totalWeight;
    delete previousUser.pendingYield;
    delete previousUser.pendingRevDis;
    delete previousUser.stakes;
    // emits an event
    emit LogMoveFundsFromWallet(
        msg.sender,
        _to,
        previousTotalWeight,
        newUser.totalWeight,
        previousYield,
        newUser.pendingYield,
        previousRevDis,
        newUser.pendingRevDis
    );
}
```

## Recommendation
Revise the above moveFundsFromWallet() function to properly migrate the stakes as well.
