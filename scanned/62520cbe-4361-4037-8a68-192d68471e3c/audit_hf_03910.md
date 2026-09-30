# [M] Only newAgent can call Agent.migrateMiner, but

## Summary
Severity: Medium
Contest weight: 0.6978
Dataset id: 20209
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
If the owner of the agent wants to upgrade the Agent instance, the owner would call AgentFactory.upgradeAgent. AgentFactory.upgradeAgent then calls oldAgent.decommissionAgent to transfer funds from old agent to new agent and set oldAgent.newAgent to the new deployed agent instance. After that, the new agent is able to call oldAgent.migrateMiner to migrate the miners. However, the new agent is not able to call migrateMiner in the current implementation. An owner of the agent can call upgradeAgent to upgrade the agent instance. It calls-glif/blob/main/pools/src/Agent/AgentFactory.sol#L51
```solidity
function upgradeAgent(
    address agent
) external returns (address newAgent) {
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
lif/blob/main/pools/src/Agent/Agent.sol#L203
```solidity
function decommissionAgent(address _newAgent) external {
    // only the agent factory can decommission an agent
    AuthController.onlyAgentFactory(router, msg.sender);
    // if the newAgent has a mismatching ID, revert
    if(IAgent(_newAgent).id() != id) revert Unauthorized();
    // set the newAgent in storage, which marks the upgrade process as starting
    newAgent = _newAgent;
    uint256 _liquidAssets = liquidAssets();
    // Withdraw all liquid funds from the Agent to the newAgent
    _poolFundsInFIL(_liquidAssets);
    // transfer funds to new agent
    payable(_newAgent).sendValue(_liquidAssets);
}
```
After AgentFactory.upgradeAgent, the new agent is able to call migrateMiner to c/Agent/Agent.sol#L217
```solidity
function migrateMiner(uint64 miner) external {
    if (newAgent != msg.sender) revert Unauthorized();
    uint256 newId = IAgent(newAgent).id();
    if (
        // first check to make sure the agentFactory knows about this "agent"
        GetRoute.agentFactory(router).agents(newAgent) != newId ||
        // then make sure this is the same agent, just upgraded
        newId != id ||
        // check to ensure this miner was registered to the original agent
        !minerRegistry.minerRegistered(id, miner)
    ) revert Unauthorized();
    // propose an ownership change (must be accepted in v2 agent)
    miner.changeOwnerAddress(newAgent);
}
```
However, it doesn’t have a method in agent.sol that can migrateMiner. It seems like this function should be called by the owner of newAgent instead of newAgent itself. Agent.migrateMiner is actually not callable.

## Recommendation
Modify the check so that the owner of the newAgent can call the function.
```solidity
function migrateMiner(uint64 miner) external {
    // if (newAgent != msg.sender) revert Unauthorized();
    if (newAgent != IAuth(newAgent).owner()) revert Unauthorized();
    uint256 newId = IAgent(newAgent).id();
    if (
        // first check to make sure the agentFactory knows about this "agent"
        GetRoute.agentFactory(router).agents(newAgent) != newId ||
        // then make sure this is the same agent, just upgraded
        newId != id ||
        // check to ensure this miner was registered to the original agent
        !minerRegistry.minerRegistered(id, miner)
    ) revert Unauthorized();
    // propose an ownership change (must be accepted in v2 agent)
    miner.changeOwnerAddress(newAgent);
}
```
