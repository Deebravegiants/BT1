# [M] Possible lost `msg.value` in `ExchangeProxy.executeSwapDirect()`.

## Summary
Severity: Medium
Chain: Smart contract
Component: 2022-10-mover
Published: 2022-10-28
Source: https://github.com/sherlock-audit/2022-10-mover-judging/issues/110
Type: sherlock-finding

## Details
hansfriese

medium

# Possible lost `msg.value` in `ExchangeProxy.executeSwapDirect()`.

## Summary
Possible lost `msg.value` in `ExchangeProxy.executeSwapDirect()`.

## Vulnerability Detail
`ExchangeProxy.executeSwapDirect()` is a `payable` function to manage both of ETH and ERC20 tokens.

```solidity
    function executeSwapDirect(
        address _beneficiary,
        address _tokenFrom,
        address _tokenTo,
        uint256 _amount,
        uint256 _exchangeFee,
        bytes memory _data
    ) public payable override returns (uint256) {
        require(msg.sender == transferProxyAddress, "transfer proxy only");

        // extract values from bytes array provided
        address executorAddress;
        address spenderAddress;
        uint256 ethValue;

        bytes memory callData = ByteUtil.slice(_data, 72, _data.length - 72);
        assembly {
            executorAddress := mload(add(_data, add(0x14, 0)))
            spenderAddress := mload(add(_data, add(0x14, 0x14)))
            ethValue := mload(add(_data, add(0x20, 0x28)))
        }

        // allow spender to transfer tokens from this contract
        if (_tokenFrom != ETH_TOKEN_ADDRESS && spenderAddress != address(0)) {
            require(trustedRegistryContract.isWhitelisted(spenderAddress), "allowance to non-trusted");
```

_Trimmed to 38 lines — full report: https://github.com/sherlock-audit/2022-10-mover-judging/issues/110_
