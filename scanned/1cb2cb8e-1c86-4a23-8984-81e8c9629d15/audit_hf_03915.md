# [M] Agent version update resets agent state

## Summary
Severity: Medium
Contest weight: 0.4425
Dataset id: 20215
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
During the agent version update, funds and some of the storage data are migrated, but the state variables faultySectorStartEpoch, administration and defaulted are not. As a result, the agent state will be reset to a good standing state. AgentFactory updates Agent to a new version by calling upgradeAgent. It does not migrate the faultySectorStartEpoch, administration and defaulted variables.
```solidity
function upgradeAgent(
    address agent
) external returns (address newAgent) {
    IAgentDeployer agDeployer = GetRoute.agentDeployer(router);
    IAgent oldAgent = IAgent(agent);
    // can only upgrade to a new version of the agent
    if (agDeployer.version() <= oldAgent.version()) revert Unauthorized();
    address owner = IAuth(address(oldAgent)).owner();
    uint256 agentId = agents[agent];
    // only the Agent's owner can upgrade (unless on administration), and only a registered agent can be upgraded
    if ((owner != msg.sender && oldAgent.administration() != msg.sender) ||
        agentId == 0) revert Unauthorized();
    // deploy a new instance of Agent with the same ID and auth
    newAgent = agDeployer.deploy(
        router,
        agentId,
        owner,
        IAuth(address(oldAgent)).operator(),
        oldAgent.adoRequestKey()
    );
    // Register the new agent and unregister the old agent
    agents[newAgent] = agentId;
    // delete the old agent from the registry
    agents[agent] = 0;
    // transfer funds from old agent to new agent and mark old agent as decommissioning
    oldAgent.decommissionAgent(newAgent);
}
```
Agent owner can reset Agent state if AgentDeployer updates its version.

## Recommendation
The faultySectorStartEpoch, administration and defaulted state variables should be migrated during agent updates.
