# [M] Checks In issue() And redeemZero()

## Summary
Severity: Medium
Contest weight: 0.4023
Dataset id: 14999
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Situation:
The functions issue() in Divider.sol#L183-231 and redeemZero() of Divider.sol have extra checks when the flags level.issueRestricted() or level.redeemZeroRestricted() are set.
In that case, the function can only be executed when called from an adapter.
The contract Periphery, specifically Periphery.sol#L410, Periphery.sol#L514, Periphery.sol#L557, calls these functions as well. However, these calls would not be allowed. The extra checks are potentially too strict.
```solidity
function issue(...) external nonReentrant whenNotPaused returns (uint256 uBal) {
    ...
    if (level.issueRestricted()) {
        require(msg.sender == adapter, Errors.IssuanceRestricted);
    }
    ...
}
function redeemZero(...) external nonReentrant whenNotPaused returns (uint256 tBal) {
    ...
    if (level.redeemZeroRestricted()) {
        require(msg.sender == adapter, Errors.RedeemZeroRestricted);
    }
}
```

## Recommendation
Double check if calling from Periphery should also be allowed.
