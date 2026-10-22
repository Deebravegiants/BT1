# [M] Back-run new deployments / front-runrefreshRoutes

## Summary
Severity: Medium
Contest weight: 0.4355
Dataset id: 20212
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Back-run new deployments / front-run refreshRoutes GLIF uses a modular system with a registry and routing to get all the contract from their codebase instead of making it upgradeable. In different contracts you have the function:
```solidity
function refreshRoutes() external {
    poolRegistry = GetRoute.poolRegistry(router);
    agentPolice = GetRoute.agentPolice(router);
    agentFactory = GetRoute.agentFactory(router);
    wFIL = GetRoute.wFIL(router);
}
```
that gets the latest deployed and registered address of the system and stores them again as storage variables of the contract this function is in. This function exists in: Agent, Agent Police, Miner Registry and Infinity Pool. When GLIF upgrades one of their contracts in this list, refreshRoutes has to be called in the same transaction to not be able to be front-runned. There are several reasons to why they want to upgrade, could be a security issues that has been patched, could be just improvements to the existing contracts. When upgrading, you are giving the opportunity to MEVs to realize that either something is wrong or there is some kind of opportunity because both contracts. Not calling refreshRoutes() at the same time you upgrade any of the contracts will open the door to this opportunities It depends on what is the reason of the upgrade from any contract upgraded. If it has had an exploit, you could still interact with it, or it might be just that you are able to profit from some states that the contract reached before upgrading

## Recommendation
Call refreshRoutes() in the same transaction that you upgrade any of the contracts
