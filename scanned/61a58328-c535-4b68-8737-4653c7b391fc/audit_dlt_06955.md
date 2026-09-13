# [M] Error in allowance logic

## Summary
Severity: Medium
Chain: Smart contract
Component: 2022-07-swivel
Published: 2022-07-15
Source: https://github.com/code-423n4/2022-07-swivel-findings/issues/129
Type: code-finding

## Details
# Lines of code

https://github.com/code-423n4/2022-07-swivel/blob/daf72892d8a8d6eaa43b9e7d1924ccb0e612ee3c/Tokens/ZcToken.sol#L112-L114
https://github.com/code-423n4/2022-07-swivel/blob/daf72892d8a8d6eaa43b9e7d1924ccb0e612ee3c/Tokens/ZcToken.sol#L132-L133


# Vulnerability details

## Impact
There is an error in the allowance functionality to allow a non-owner to withdraw or redeem ZcTokens for the owner. Taking `ZcToken.redeem()` as an example, behold the following if/else block:

```
        if (holder == msg.sender) {
            return redeemer.authRedeem(protocol, underlying, maturity, msg.sender, receiver, principalAmount);
        }
        else {
            uint256 allowed = allowance[holder][msg.sender];
            if (allowed >= principalAmount) { revert Approvals(allowed, principalAmount); }
            allowance[holder][msg.sender] -= principalAmount;  
            return redeemer.authRedeem(protocol, underlying, maturity, holder, receiver, principalAmount);
```

If the `msg.sender` is the holder, no check for allowance is needed. If the sender is not the holder, then their allowance is checked.

The error lies in the if statement `if (allowed >= principalAmount) { revert Approvals(allowed, principalAmount); }`. This states that if the sender has equal to or more allowance than the principalAmount, revert.

Therefore, if the sender has the proper allowance or more allowance than necessary, the transaction will revert. If the sender has less allowance than necessary, the transaction will still revert because of the `allowance[holder][msg.sender] -= principalAmount;` clause.

In conclusion, there is no way to `withdraw()` or `redeem()` on behalf of another user.

## Tools Used
Manual review.

## Recommended Mitigation Steps
The fix is to simply change `>=` to `<`
