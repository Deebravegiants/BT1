# [H] L1 CCIP messages use incorrect `tokensInTransitToL1` value leading to overvalued LST on Metis

## Summary
Severity: High
Contest weight: 0.9768
Dataset id: 22224
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
A discrepancy in withdrawal accounting between L1 and L2 chains can lead to an artificial inflation of the share price in the staking system.

In the `L1Transmitter::_executeUpdate` function, note that while actual amount withdrawn from `L1Strategy` is `toWithdraw`, the CCIP message assumes that the full `queuedWithdrawals` is withdrawn. In the scenario where `queuedWithdrawals > canWithdraw`, the CCIP message is sending an inflated value for `tokensInTransitToL1`

```solidity
//L1Transmitter.sol
function _executeUpdate() private {
    // ...
    uint256 toWithdraw = queuedWithdrawals > canWithdraw ? canWithdraw : queuedWithdrawals;
    if (toWithdraw > minWithdrawalThreshold) { //@audit only when amount > min withdrawal
        l1Strategy.withdraw(toWithdraw); //@audit actual amount withdrawn is toWithdraw
        // ... (withdrawal logic)
    }

    Client.EVM2AnyMessage memory evm2AnyMessage = _buildCCIPUpdateMessage(
        totalDeposits,
        claimedRewards + queuedWithdrawals,  // @audit This uses full queuedWithdrawals, not actual withdrawn amount
        depositsSinceLastUpdate,
        opRewardReceivers,
        opRewardAmounts
    );
    // ...
}
```

In L2Transmitter.sol, the inflated withdrawal amount (`tokensInTransitFromL1`) is accepted without validation:

```solidity
//L2Transmitter.sol
function _ccipReceive(Client.Any2EVMMessage memory _message) internal override {
    // ...
    (
        uint256 totalDeposits,
        uint256 tokensInTransitFromL1,
        uint256 tokensReceivedAtL1,
        address[] memory opRewardReceivers,
        uint256[] memory opRewardAmounts
    ) = abi.decode(_message.data, (uint256, uint256, uint256, address[], uint256[]));

    l2Strategy.handleUpdateFromL1(
        totalDeposits,
        tokensInTransitFromL1,  //@audit This value could be inflated
        tokensReceivedAtL1,
        opRewardReceivers,
        opRewardAmounts
    );
    // ...
}
```

3. In L2Strategy.sol, the inflated tokensInTransitFromL1 inflates deposit change calculations:
```solidity
function getDepositChange() public view returns (int) {
    return
        int256(
            l1TotalDeposits +
                tokensInTransitToL1 +
                tokensInTransitFromL1 +  //@audit This value could be inflated
                token.balanceOf(address(this))
        ) - int256(totalDeposits);
}
```
4. Finally, in StakingPool.sol, the inflated deposit change leads to an artificial increase in totalRewards and share price:
```solidity
function _updateStrategyRewards(uint256[] memory _strategyIdxs, bytes memory _data) private {
    int256 totalRewards;
    // ...
    for (uint256 i = 0; i < _strategyIdxs.length; ++i) {
        IStrategy strategy = IStrategy(strategies[_strategyIdxs[i]]);
        (int256 depositChange, , ) = strategy.updateDeposits(_data);
        totalRewards += depositChange;
    }

    if (totalRewards != 0) {
        totalStaked = uint256(int256(totalStaked) + totalRewards);
    }
    // ...
}
```
This vulnerability leads to an inflate share price of the liquid staking token.

## Recommendation
Ensure accurate tracking of actual withdrawn amounts on L1:

```solidity
uint256 actualWithdrawn = 0;
if (toWithdraw > minWithdrawalThreshold) {
    l1Strategy.withdraw(toWithdraw);
    actualWithdrawn = toWithdraw;
    // ... (rest of withdrawal logic)
}
```
Use the actual withdrawn amount in the CCIP message to L2:
```solidity
Client.EVM2AnyMessage memory evm2AnyMessage = _buildCCIPUpdateMessage(
    totalDeposits,
    claimedRewards + actualWithdrawn,
    depositsSinceLastUpdate,
    opRewardReceivers,
    opRewardAmounts
);
```
