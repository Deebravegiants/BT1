# [M] Deployer fees cannot be higher than 255 basis points

## Summary
Severity: Medium
Contest weight: 0.5444
Dataset id: 8344
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
g8keepFactory.deployToken function allows the deployer to set the buy and sell fees for the token. Initially, the maximum value for these fees is 500 basis points. However, the function signature uses uint8 for these values, which means that the maximum value that can be set is 255 basis points. This means that the deployer cannot set fees higher than 255 basis points.
```solidity
function deployToken(
    uint256 _initialLiquidity,
    string memory _name,
    string memory _symbol,
    uint256 _totalSupply,
    address _treasuryWallet,
    uint8 _buyFee,
    uint8 _sellFee,
```

## Recommendation
```solidity
function deployToken(
    uint256 _initialLiquidity,
    string memory _name,
    string memory _symbol,
    uint256 _totalSupply,
    address _treasuryWallet,
    uint16 _buyFee,
    uint16 _sellFee,
```
