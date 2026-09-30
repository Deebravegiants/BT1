# [M] XERC20 does not work on Super-

## Summary
Severity: Medium
Contest weight: 0.5818
Dataset id: 1811
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The Superchain's interfaces and events used within the XERC20 are outdated. As a result, existing XVELO will not work on Superchain in its current form.
The Superchain's interfaces and events used within the in-scope XERC20 are outdated.
In-scope XERC20
Superchain's Spec
```solidity
__crosschainMint(address _to, uint256 _amount)
crosschainMint(address _account, uint256 _amount)
__crosschainBurn(address _from, uint256 _amount)
crosschainBurn(address _account, uint256 _amount)
emit CrosschainMinted(address indexed _to, uint256 _amount);
event CrosschainMint(address indexed _to, uint256 _amount)
emit CrosschainBurnt(address indexed _from, uint256 _amount);
event CrosschainBurn(address indexed _from, uint256 _amount)
```
c871e6a6ecd7c5403d/superchain-contracts-private/src/xerc20/XERC20.sol#L173
File: XERC20.sol
172:
```solidity
/// @inheritdoc ICrosschainERC20
```
173:
```solidity
function __crosschainMint(address _to, uint256 _amount) external onlySuperchainERC20Bridge {
    _depleteBuffer(msg.sender, _amount);
    _mint(_to, _amount);

    emit CrosschainMinted(_to, _amount);
}
```
179:
```solidity
/// @inheritdoc ICrosschainERC20
```
180:
```solidity
function __crosschainBurn(address _from, uint256 _amount) external onlySuperchainERC20Bridge {
    _spendAllowance(_from, msg.sender, _amount);
    _replenishBuffer(msg.sender, _amount);
    _burn(_from, _amount);

    emit CrosschainBurnt(_from, _amount);
}
```
The existing XVELO will not work on Superchain in its current form.

## Recommendation
Consider updating the XERC20's interfaces and events to the latest Superchain Specification.
Per Optimism’s documentation as of 24 October 2024:
Interop is currently in active development and not yet ready for production use. The information provided here may change. Check back regularly for the most up-to-date information.
Thus, it is recommended to verify the finality of the SuperchainERC20 Token Standard again before XVELO deployment to ensure that there are no further changes expected
