# [H] Winning agent id may be uninitialized when

## Summary
Severity: High
Contest weight: 0.5476
Dataset id: 20371
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
We can see in the implementation of claimGrandPrize that: on/contracts/Infiltration.sol#L658 The field Agent.agentId of the struct is used to determine if the caller can claim. Since the id is zero, and it is and invalid id for an agent, there is no owner for it and the condition: on/contracts/Infiltration.sol#L1666-L1670 Always reverts. The grand prize ends up locked/unclaimable by the winner

## Recommendation
In claimGrandPrize use 1 as the default if agents[1].agentId == 0:
```solidity
function claimGrandPrize() external nonReentrant {
    _assertGameOver();
    uint256 agentId = agents[1].agentId;
    if (agentId == 0)
        agentId = 1;
    _assertAgentOwnership(agentId);
    uint256 prizePool = gameInfo.prizePool;
    if (prizePool == 0) {
        revert NothingToClaim();
    }
    gameInfo.prizePool = 0;
    _transferETHAndWrapIfFailWithGasLimit(WETH, msg.sender, prizePool, gasleft());
    emit PrizeClaimed(agentId, address(0), prizePool);
}
```
