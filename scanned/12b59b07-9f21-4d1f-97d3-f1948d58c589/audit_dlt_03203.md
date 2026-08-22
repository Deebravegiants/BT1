# [M] function changeController() has rug potential as admin can unilaterally withdraw all user funds from both risk and insure vaults

## Summary
Severity: Medium
Chain: Smart contract
Component: 2022-09-y2k-finance
Published: 2022-09-19
Source: https://github.com/code-423n4/2022-09-y2k-finance-findings/issues/269
Type: code-finding

## Details
# Lines of code

https://github.com/code-423n4/2022-09-y2k-finance/blob/2175c044af98509261e4147edeb48e1036773771/src/Vault.sol#L295
https://github.com/code-423n4/2022-09-y2k-finance/blob/2175c044af98509261e4147edeb48e1036773771/src/Vault.sol#L360-L366


# Vulnerability details

## Impact

Admin can rug all user funds in every vaults deployed by changing the controller address.

## Proof of Concept

Controller can be changed by admin anytime without any warning to users. 

[Vault.sol#L295](https://github.com/code-423n4/2022-09-y2k-finance/blob/2175c044af98509261e4147edeb48e1036773771/src/Vault.sol#L295)
```solidity
    function changeController(address _controller) public onlyFactory {
        if(_controller == address(0))
            revert AddressZero();
        controller = _controller;
    }
```
Tokens in the vaults can then be called by the malicious contract to be transferred to their own address with `sendTokens()`.

[Vault.sol#L360-L366](https://github.com/code-423n4/2022-09-y2k-finance/blob/2175c044af98509261e4147edeb48e1036773771/src/Vault.sol#L360-L366)
```solidity
    function sendTokens(uint256 id, address _counterparty)
        public
        onlyController
        marketExists(id)
    {
        asset.transfer(_counterparty, idFinalTVL[id]);
    }
```

## Recommended Mitigation Steps

_Trimmed to 38 lines — full report: https://github.com/code-423n4/2022-09-y2k-finance-findings/issues/269_
