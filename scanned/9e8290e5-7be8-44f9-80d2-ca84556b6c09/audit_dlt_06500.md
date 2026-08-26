# [M] Unauthorized access to `Governor_v1.acceptOwnership()` function which breaks protocol intended design

## Summary
Severity: Medium
Chain: Smart contract
Component: Inverter-Network
Published: 2024-06-07
Source: https://github.com/hats-finance/Inverter-Network-0xe47e52c4fea05e555920f1dcdcc6fb8eca103eeb/issues/60
Type: hats-finding

## Details
**Github username:** @0xRizwan
**Twitter username:** 0xRizwann
**Submission hash (on-chain):** 0x2889a8ca6e565def4db0ec6b469ec5dbacad47ea89830b304f2a62d328aa89c0
**Severity:** medium

**Description:**
**Description**\
`Governor_v1.acceptOwnership()` is used to accept the ownership of other contracts if these contracts transfer their ownership to it. This is acheived by openzeppelin's ownable2step contract. `Governor_v1.acceptOwnership()` is implemented as:

```solidity
    function acceptOwnership(address adr)
        external
        onlyCommunityOrTeamMultisig
    {
        if (adr.code.length == 0) {
            revert Governor__CallToTargetContractFailed();
        }

        (bool success,) =
            adr.call(abi.encodeCall(Ownable2Step.acceptOwnership, ()));

        // if the call is not a success
        if (!success) {
            revert Governor__CallToTargetContractFailed();
        }
        emit OwnershipAccepted(adr);
    }
```
acceptOwnership() can only be accessed by `onlyCommunityOrTeamMultisig` which means either `COMMUNITY_MULTISIG_ROLE` address OR `TEAM_MULTISIG_ROLE` address are allowed to accces it to accept the ownership of contracts.

but, the `acceptOwnership()` Natspec in interface states that only `COMMUNITY_MULTISIG_ROLE` is allowed to access it.

```solidity
    /// @notice Accepts the ownership over the target address
@>  /// @dev can only be accessed by the COMMUNITY_MULTISIG_ROLE
    /// @param adr The address of target that wants to hand over the ownership
    function acceptOwnership(address adr) external;
```

_Trimmed to 38 lines — full report: https://github.com/hats-finance/Inverter-Network-0xe47e52c4fea05e555920f1dcdcc6fb8eca103eeb/issues/60_
