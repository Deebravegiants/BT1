# [M] Agent owners can lose funds if agent is up-

## Summary
Severity: Medium
Contest weight: 0.1770
Dataset id: 20214
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
consider the following scenario: Alice is an agent owner. The agent is in debt to the pool so Alice decides to transfer funds to agent and then call the pay function. Just before (or in the same block) Alice sends the funds, a new agent version is made and updateAgent is called. Once an update happens, almost all operations are frozen on the old agent by the checkVersion modifier. The transferred funds will be locked in the old agent without the ability to migrate them to the new agent. Almost all operations in the agent require that there is no new agent version t/Agent.sol#L535
function _checkVersion() internal view {
    if (GetRoute.agentDeployer(router).version() != version) revert BadAgentState();
}
Once agentDeployer is updated to include a new version, no critical operations can happen. The agent can be updated by the owner or by the administration. It is reasonable to assume upgradeAgent can happen automatically. For example, the protocol could have an automated script to update all agents that are on administration OR the user can have a config enabled in the agent cli to automatically update. Once the agent is updated. There is no way to send funds to the new agent. Any funds send to the agent after update will be permanently locked.

## Recommendation
Similar to allowing migration of miners to the new agent, implement a function that allows the owner to migrate funds to the new agent.
