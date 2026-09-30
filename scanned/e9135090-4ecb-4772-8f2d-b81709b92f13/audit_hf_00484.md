# [M] Attacker can revoke any user

## Summary
Severity: Medium
Contest weight: 0.4036
Dataset id: 1926
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Lack of access control in revokeLender allows an attacker to revoke any participant from a market
The delegation version of the revokeLender function fails to perform any access control checks allowing any user to revoke any user
```solidity
function _revokeStakeholderViaDelegation(
    uint256 _marketId,
    address _stakeholderAddress,
    bool _isLender,
    uint8 _v,
    bytes32 _r,
    bytes32 _s
) internal {
    bytes32 uuid = _revokeStakeholderVerification(
        _marketId,
        _stakeholderAddress,
        _isLender
    );
    //
    address attestor = markets[_marketId].owner;
    //
    tellerAS.revokeByDelegation(uuid, attestor, _v, _r, _s);
}
```
Internal pre-conditions
Attestation should be enabled to observe the impact
External pre-conditions
Attack Path
1. Attacker calls revokeLender by passing in any address they wish to revoke from the market
Attacker can revoke any address they wish from any market making the market unuseable

## Recommendation
Perform access control checks
