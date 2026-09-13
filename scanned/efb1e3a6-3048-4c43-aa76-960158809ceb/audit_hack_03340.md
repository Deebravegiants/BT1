# [M] Use of .transfer()

## Summary
Severity: Medium
Reporter: defsec
Source: https://github.com/sherlock-audit/2022-11-dodo/blob/main/contracts/SmartRoute/lib/UniversalERC20.sol#L29
Type: audit-issue

## Details
# Use of .transfer()

## Summary

The use of transfer() to send ETH only forwards 2300 gas to the recipient. This is not enough gas to execute a gnosis safe delegatecall. Funds can be lost in such a situation or similar edge cases.


## Vulnerability Detail

The use of transfer() to send ETH only forwards 2300 gas to the recipient. This is not enough gas to execute a gnosis safe delegatecall. Funds can be lost in such a situation or similar edge cases.

## Impact

Transfer will revert

## Code Snippet

https://github.com/sherlock-audit/2022-11-dodo/blob/main/contracts/SmartRoute/lib/UniversalERC20.sol#L29


```solidity
    function universalTransfer(
        IERC20 token,
        address payable to,
        uint256 amount
    ) internal {
        if (amount > 0) {
            if (isETH(token)) {
                to.transfer(amount);
            } else {
                token.safeTransfer(to, amount);
            }
        }
    }
```


## Tool used

Manual Review

## Recommendation

I recommend changing to .call() with fixed gas. I believe 30000 to be a nice amount with little risk of:

- EIPs increasing op code gas costs exceeding the value.
- Reentrancy.
