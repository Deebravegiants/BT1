# [H] `ConvexStakingWrapper.exitShelter

## Summary
Severity: High
Contest weight: 0.8406
Dataset id: 1554
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The shelter mechanism provides emergency functionality in an effort to protect users’ funds. The `enterShelter` function will withdraw all LP tokens from the pool, transfer them to the shelter contract and activate the shelter for the target LP token. Conversely, the `exitShelter` function will deactivate the shelter and transfer all LP tokens back to the `ConvexStakingWrapper.sol` contract.

Unfortunately, LP tokens aren’t restaked in the pool, causing LP tokens to be stuck within the contract. Users will be unable to withdraw their LP tokens as the `withdraw` function attempts to `withdrawAndUnwrap` LP tokens from the staking pool. As a result, this function will always revert due to insufficient staked balance. If other users decide to deposit their LP tokens, then these tokens can be swiped by users who have had their LP tokens locked in the contract.

This guarantees poor UX for the protocol and will most definitely lead to LP token loss.

## Proof of Concept
[ConvexStakingWrapper.sol#L121-L130](https://github.com/code-423n4/2022-02-concur/blob/shelter-client/contracts/ConvexStakingWrapper.sol#L121-L130)

```solidity
function exitShelter(uint256[] calldata _pids) external onlyOwner {
    for(uint256 i = 0; i<_pids.length; i++){
        IRewardStaking pool = IRewardStaking(convexPool[_pids[i]]);
        IERC20 lpToken = IERC20(
            pool.poolInfo(_pids[i]).lptoken
        );
        amountInShelter[lpToken] = 0;
        shelter.deactivate(lpToken);
    }
}
```

[ConvexStakingWrapper.sol#L309-L331](https://github.com/code-423n4/2022-02-concur/blob/shelter-client/contracts/ConvexStakingWrapper.sol#L309-L331)

```solidity
function withdraw(uint256 _pid, uint256 _amount)
    external
    nonReentrant
    whenNotInShelter(_pid)
{
    WithdrawRequest memory request = withdrawRequest[_pid][msg.sender];
    require(request.epoch < currentEpoch() && deposits[_pid][msg.sender].epoch + 1 < currentEpoch(), "wait");
    require(request.amount >= _amount, "too much");
    _checkpoint(_pid, msg.sender);
    deposits[_pid][msg.sender].amount -= uint192(_amount);
    if (_amount > 0) {
        IRewardStaking(convexPool[_pid]).withdrawAndUnwrap(_amount, false);
        IERC20 lpToken = IERC20(
            IRewardStaking(convexPool[_pid]).poolInfo(_pid).lptoken
        );
        lpToken.safeTransfer(msg.sender, _amount);
        uint256 pid = masterChef.pid(address(lpToken));
        masterChef.withdraw(msg.sender, pid, _amount);
    }
    delete withdrawRequest[_pid][msg.sender];
    //events
    emit Withdrawn(msg.sender, _amount);
}
```

## Recommendation
Consider re-depositing LP tokens upon calling `exitShelter`. This should ensure the same tokens can be reclaimed by users wishing to exit the `ConvexStakingWrapper.sol` contract.

The warden has identified how through a combination of using the shelter and sending funds back, the funds would actually end up being stuck and non-withdrawable by depositors.

I believe that generally speaking this would be a Medium Severity finding as the funds would be stuck if the sponsor were to activate the shelter and then send the tokens back (conditionality).

However, the warden has shown that the system of Contract + Shelter is effectively broken, and for this reason I believe the finding is of High Severity.
