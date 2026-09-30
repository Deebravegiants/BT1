# [M] Error in allowance logic

## Summary
Severity: Medium
Contest weight: 0.4377
Dataset id: 15807
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
There is an error in the allowance functionality to allow a non-owner to withdraw or redeem ZcTokens for the owner. Taking `ZcToken.redeem()` as an example, behold the following if/else block:
    
```solidity
if (holder == msg.sender) {
    return redeemer.authRedeem(protocol, underlying, maturity, msg.sender, receiver, principalAmount);
}
else {
    uint256 allowed = allowance[holder][msg.sender];
    if (allowed >= principalAmount) { revert Approvals(allowed, principalAmount); }
    allowance[holder][msg.sender] -= principalAmount;  
    return redeemer.authRedeem(protocol, underlying, maturity, holder, receiver, principalAmount);
}
```

If the `msg.sender` is the holder, no check for allowance is needed. If the sender is not the holder, then their allowance is checked.

The error lies in the if statement `if (allowed >= principalAmount) { revert Approvals(allowed, principalAmount); }`. This states that if the sender has equal to or more allowance than the principalAmount, revert.

Therefore, if the sender has the proper allowance or more allowance than necessary, the transaction will revert. If the sender has less allowance than necessary, the transaction will still revert because of the `allowance[holder][msg.sender] -= principalAmount;` clause.

In conclusion, there is no way to `withdraw()` or `redeem()` on behalf of another user.

## Recommendation
The fix is to simply change `>=` to `<`.

Approval workflow doesnt leave funds at risk but is a nice to have, that plus scope and this _might_ end up Low risk but I think Medium is appropriate as well.

This is a good issue and I agree with the severity. I decided against making this High severity due to the fact that funds are not necessarily at risk; it’s just intended allowance functionality will not behave as expected. 

See [#180](https://github.com/code-423n4/2022-07-swivel-findings/issues/180). 

Making this the main issue for the allowance flipped sign.
