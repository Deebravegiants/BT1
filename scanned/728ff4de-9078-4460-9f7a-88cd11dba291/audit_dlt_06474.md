# [H] Sandwich attacks can empty `FundingManager` upon owner set virtual supply changes

## Summary
Severity: High
Chain: Smart contract
Component: Inverter-Network
Published: 2024-06-18
Source: https://github.com/hats-finance/Inverter-Network-0xe47e52c4fea05e555920f1dcdcc6fb8eca103eeb/issues/155
Type: hats-finding

## Details
**Github username:** @0xfuje
**Twitter username:** 0xfuje
**Submission hash (on-chain):** 0xbc05ca83aef5a2599fc1c89743a3e255bea8562a89d7a7b6a579cdbd9367cb96
**Severity:** high

**Description:**
## Impact
Potential total loss of collateral funds in `BondingCurve` `FundingManager`.

## Description
The problem is that the `FundingManager`'s balance does not necessarily reflect it's virtual `collateral` and `issuance` supply. When these values are changed without organic `buy` and `sell` orders via `setVirtualCollateralSupply()` or `setVirtualIssuanceSupply()`, the total amount of change can be sandwiched risk-free by an attacker.



`FM_BC_Bancor_Redeeming_VirtualSupply_v1` - `setVirtualCollateralSupply()`
```solidity
    function setVirtualCollateralSupply(uint _virtualSupply)
        external
        virtual
        override(VirtualCollateralSupplyBase_v1)
        onlyOrchestratorAdmin
    {
        _setVirtualCollateralSupply(_virtualSupply);
    }
```


## Attack scenario
This is just a specific scenario, the issue affects `setVirtualIssuanceSupply` as well and is meant to be a general submission for sandwich attacks regarding owner set virtual supply changes.

1. Funding manager is initialized 
2. Users fund the funding manager and mint `issuance` tokens via `buyOrders` up to `100e18` of `collateral` tokens
3. This means current virtual collateral supply is at `100e18`
4. Orchestrator owner raises the collateral supply to `10000e18` via `setVirtualCollateralSupply` (e.g. plans to manually transfer those tokens after this TX so payment based modules can have enough funds to take from `FM`)
5. Attacker front-runs `setVirtualCollateralSupply` with a minimal amount of `1.1e18` `buyOrder()`, note that this will be worth substantially more after the new collateral supply has been set
6. Owner's tx executes and collateral supply has been raised
7. Attacker back-runs with a sell off of their recently bought `issuance` tokens, which will empty the `FundingManager` almost completely


_Trimmed to 38 lines — full report: https://github.com/hats-finance/Inverter-Network-0xe47e52c4fea05e555920f1dcdcc6fb8eca103eeb/issues/155_
