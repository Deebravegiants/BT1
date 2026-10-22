# [M] Agent can prevent liquidation/administration/default

## Summary
Severity: Medium
Contest weight: 0.5821
Dataset id: 20218
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
There is not cap to the amount of pools an agent can register to. When the platform will support multiple pools, and agent can register to all of them and cause an out of gas error when the agentPolice iterates over them. supported this vulnerability will exist. There is no cap to the amount of pools an agent can borrow from. https://github.co
```solidity
function addPoolToList(uint256 agentID, uint256 pool) external onlyPool(pool) {
    _poolIDs[agentID].push(pool);
}
```
The above function gets called by a pool when the agent borrows from it. An agent can borrow a very small amount from all the pools available in the PoolRegistry. This is an issue since the agentPolice cannot iterate over a large number of pools as it will consume a lot of gas an potentially more then the allowed block gas limit in filecoin. The agent needs to iterate over the agent pools when it needs to liquidate/default or put the agent on administration. This is done through the onlyWhenBehindTargetEpoch modifier:
```solidity
modifier onlyWhenBehindTargetEpoch(address agent) {
    if (!_epochsPaidBehindTarget(IAgent(agent).id(), defaultWindow)) {
        revert Unauthorized();
    }
    _;
}
```
```solidity
function _epochsPaidBehindTarget(
    uint256 _agentID,
    uint256 _targetEpoch
) internal view returns (bool) {
    uint256[] memory pools = poolRegistry.poolIDs(_agentID);
    revert out of gas
    if (AccountHelpers.getAccount(router, _agentID, pools[i]).epochsPaid <
        block.number - _targetEpoch) {
        return true;
    }
}
return false;
```
the agent can freely borrow and not payup in time without being defaulted/adminstration/liquidated. Leading to loss of pool funds

## Recommendation
Set a limit to the amount of pools that can be borrowed against.
