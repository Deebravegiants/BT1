# [H] When proxy/owner call `executeFlashLoans` they can steal funds

## Summary
Severity: High
Reporter: simon135
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
# When proxy/owner call `executeFlashLoans` they can steal funds

## Summary
since there is no check on the parameters in the function an owner/proxy role can come and steal the funds 
## Vulnerability Detail
Repesnt example:
Alice deposits 100 usdc in the contract
Proxy role/owner comes and makes tx with `executeFlashLoans->_swapApproveTarget` their address and then they steal the funds and close the flash loan with a little fee.
## Impact
funds lost / opening of debts
## Code Snippet
```solidity
  IERC20(_swapApproveToken[i]).approve(_swapApproveTarget, type(uint256).max);
```

## Tool used

Manual Review

## Recommendation
Check `swapApproveTarget`
