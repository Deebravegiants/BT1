# [M] the swap will fail on `ExchangeProxy.sol`

## Summary
Severity: Medium
Chain: Smart contract
Component: 2022-10-mover
Published: 2022-10-28
Source: https://github.com/sherlock-audit/2022-10-mover-judging/issues/75
Type: sherlock-finding

## Details
Ch_301

medium

# the swap will fail on `ExchangeProxy.sol`

## Summary
No one can execute a swap by invoking `executeSwap()`

## Vulnerability Detail
On `ExchangeProxy.sol` == >`executeSwapDirect()`

```solidity
        require(msg.sender == transferProxyAddress, "transfer proxy only");
```

So only `transferProxyAddress` can invoke `executeSwapDirect()`
But `executeSwap()` on `ExchangeProxy.sol` has an invoke to `executeSwapDirect()`

```solidity
return executeSwapDirect(msg.sender, _tokenFrom, _tokenTo, _amount, 0, _data);
```

## Impact
No one can invoke `executeSwap()` successfully it will always revert 

## Code Snippet
```solidity
   function executeSwap(
        address _tokenFrom,
        address _tokenTo,
        uint256 _amount,
        bytes memory _data
    ) public payable override returns (uint256) {
        // native token doesn't need to be transferred explicitly, it's in tx.value
        if (_tokenFrom != ETH_TOKEN_ADDRESS) {
            IERC20(_tokenFrom).safeTransferFrom(msg.sender, address(this), _amount);
        }
```

_Trimmed to 38 lines — full report: https://github.com/sherlock-audit/2022-10-mover-judging/issues/75_
