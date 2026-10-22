# [M] Non-ERC20 tokens are not supported as paired tokens

## Summary
Severity: Medium
Contest weight: 0.3806
Dataset id: 8347
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In order to transfer funds from the deployer to the factory, g8keepFactory.deployToken() function uses erc20 transferFrom() function.
```solidity
IERC20(_pairedToken).transferFrom(msg.sender, address(this), _initialLiquidity);
```
In case if there is a need to add non erc20 token as a paired token, then such a call will revert, thus such tokens are not supported by the factory.
Another place in the code, where erc20 functions are used is g8keepFactory.withdrawToken and g8keepToken.withdrawToken functions.
Those functions won't work with non erc20 tokens as well.

## Recommendation
Use SafeERC20 or a similar library.
