# [H] Any module can drain the  `FundingManager` of all funding tokens

## Summary
Severity: High
Chain: Smart contract
Component: Inverter-Network
Published: 2024-06-06
Source: https://github.com/hats-finance/Inverter-Network-0xe47e52c4fea05e555920f1dcdcc6fb8eca103eeb/issues/50
Type: hats-finding

## Details
**Github username:** @0xfuje
**Twitter username:** 0xfuje
**Submission hash (on-chain):** 0x27f9021e3e442d34e67a69b9a37ea9c2ced9687f68e4db5a719b6b3b148e9eae
**Severity:** high

**Description:**
## Impact
Massive loss of user / orchestrator funds: attacker can transfer every `FundingManager` orchestrator token to themselves

## Description
This vulnerability arises with a combination of two weaknesses of the system.

### 1. Every module has the same permission to call as the orchestrator owner
The `Orchestrator_v1` contract inherits `ModuleManagerBase_v1`. The owner of the orchestrator contract has the power to make any calls to any contracts via the `executeTx` function.

`Orchestrator_v1` - `executeTx()`
```solidity
    function executeTx(address target, bytes memory data)
        external
        onlyOrchestratorOwner
        returns (bytes memory)
    {
        bool ok;
        bytes memory returnData;
        (ok, returnData) = target.call(data);

        if (ok) {
            return returnData;
        } else {
            revert Orchestrator__ExecuteTxFailed();
        }
    }
```
However, any module has the same permissions as well via using `executeTxFromModule()`, which should not be the case. This means that any module can pose as the orchestrator address as the `msg.sender`.

`ModuleManagerBase_v1` - `executeTxFromModule()`
```solidity
    function executeTxFromModule(
```

_Trimmed to 38 lines — full report: https://github.com/hats-finance/Inverter-Network-0xe47e52c4fea05e555920f1dcdcc6fb8eca103eeb/issues/50_
