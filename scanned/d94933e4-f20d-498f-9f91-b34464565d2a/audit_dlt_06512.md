# [H] Reorg issues in factories lead to loss of funds for users

## Summary
Severity: High
Chain: Smart contract
Component: Inverter-Network
Published: 2024-06-05
Source: https://github.com/hats-finance/Inverter-Network-0xe47e52c4fea05e555920f1dcdcc6fb8eca103eeb/issues/18
Type: hats-finding

## Details
**Github username:** --
**Twitter username:** --
**Submission hash (on-chain):** 0xd349877d4ad392880c37d60c2a9e9c49384304089da69516959c4a37dc7f37c5
**Severity:** high

**Description:**
**Description**\
As the protocol plan to deploy on Polygon, where reorgs are common occurence and happen with an average depth of 15-20 per day, it is very important to be careful for reorg specific issues. Protocol is using factories to depoloy `orchestrators` and `modules`. Those factories are using [create](https://www.immunebytes.com/blog/explained-create2-opcode-in-solidity/) optoce for this action, which only consider factory nonce. This is very dangerous especially because deployed modules may hold funds -> `deposit`, which may lead to users loosing those. If a user deploy an orchestrator with a funding manager module, then deposit some funds to the funding manager in different transaction and reorg occur, this can lead to his funds being stolen.
[Reorgs article](https://abarbatei.xyz/blockchain-reorgs-for-managers-and-auditors)

**Attack Scenario**\
1. Bob calls `OrchestratorFactory_v1::createOrchestrator` with params
2. This transaction is deploying new `fundingManager` using `ModuleFactory_v1` -> using `create` optcode from OZ's `clone` implementation, which means that the address is deterministic
3. Bob then want to fund his `FM_Rebasing_v1` and calls `FM_Rebasing_v1::deposit` in the following block
4. But then Eve sees that reorg is going to happen and front-run his `OrchestratorFactory_v1::createOrchestrator` with an auth config, which has configured for address as owner. `ModuleFactory_v1` deploys `FM_Rebasing_v1` on the same address that Bob's earlier transaction.
5. Then Bob's deposit transaction is done in Eve's Manager and she can instantly execute `FM_Rebasing_v1::transferOrchestratorToken` trough her orchestrator `executeTx` function

**Attachments**

1. **Proof of Concept (PoC) File**

2. **Revised Code File (Optional)**
Use `create2` when deploying new module instances using `msg.sender` as salt
