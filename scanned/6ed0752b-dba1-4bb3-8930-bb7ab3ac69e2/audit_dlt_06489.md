# [M] Upgradeable contracts pattern is corruptible for some contracts

## Summary
Severity: Medium
Chain: Smart contract
Component: Inverter-Network
Published: 2024-06-09
Source: https://github.com/hats-finance/Inverter-Network-0xe47e52c4fea05e555920f1dcdcc6fb8eca103eeb/issues/84
Type: hats-finding

## Details
**Github username:** @0xRizwan
**Twitter username:** 0xRizwann
**Submission hash (on-chain):** 0xbd730fdbfcaf76a08dd0710c391ead4285899ac345af766f72312ea544fe40a8
**Severity:** medium

**Description:**
**Description**\

For upgradeable contracts, there must be storage gap to "allow developers to freely add new state variables in the future without compromising the storage compatibility with existing deployments". Otherwise it may be very difficult to write new implementation code. Without storage gap, the variable in child contract might be overwritten by the upgraded base contract if new variables are added to the base contract. This could have unintended and very serious consequences to the child contracts which potentially causing the contract to malfunctions.

Below are few issues identified in Inverter contracts:

1) `Orchestrator_v1.sol` is an upgradeable contract which has used base contract `ModuleManagerBase_v1`. This contracts has implemented Storage gap. `ModuleManagerBase_v1` is only expected to be used as base contract of upgradeable contract but the base contracts or contracts inherited by it from openzeppelin are not upgradeable which means contracts inherited by it has missing storage gaps.

```solidity
abstract contract ModuleManagerBase_v1 is
    IModuleManagerBase_v1,
    Initializable,
    ERC2771Context,
    ERC165
{
```

Without gaps, adding new storage variables to any of these contracts can potentially overwrite the beginning of the storage layout of the child contract, causing critical misbehaviors in the system, Therefore, upgradeable contract must be imported from openzeppelin which are explicitely used in upgradeable contracts instead of non-upgradeable contracts as used in current implementation.

****Recommendation to fix**\
Consider below changes in `ModuleManagerBase_v1.sol`:

```diff
// External Dependencies
- import {ERC2771Context} from "@oz/metatx/ERC2771Context.sol";
+ import {ERC2771ContextUpgradeable,ContextUpgradeable} from "@oz-up/metatx/ERC2771ContextUpgradeable.sol";
import {Initializable} from "@oz-up/proxy/utils/Initializable.sol";
import {ERC165} from "@oz/utils/introspection/ERC165.sol";



  . . . some code
```

_Trimmed to 38 lines — full report: https://github.com/hats-finance/Inverter-Network-0xe47e52c4fea05e555920f1dcdcc6fb8eca103eeb/issues/84_
