# [M] status of referral code is al-

## Summary
Severity: Medium
Contest weight: 0.4089
Dataset id: 1767
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In updateReferral function in Referral.sol is setting the status of the referral code to true irrespective of the passed value. But when false is passed it should change the status of the referral code to false.
In updateReferral function in Referral.sol:200 is setting the status of the referral code always to true irrespective of the passed boolean value.
Internal pre-conditions
None
External pre-conditions
None
Attack Path
1. Handler first set the status of Referral code ALICE to private by calling updateReferral(ALICE,true).
2. Now after some time handler needs to set the status of the code from private to normal for some reason.
3. Now handler calls updateReferral(ALICE,false) but status of the code will not be set to public because updateReferral is always setting the status of code to true irrespective of the value passed.
Referral code statuses cannot be set to public from private.

## Recommendation
Instead of setting to true set the provided bool
```solidity
function updateReferral(bytes32 _code, bool _isPrivate) external onlyGovOrHandler {
    require(_code != bytes32(0), "Referral: invalid _code");
    require(codeOwners[_code] != address(0), "Referral: Code Owner Does Not Exist");
    isPrivate[_code] = _isPrivate;
    emit CodeUpdated(_code, _isPrivate);
}
```
