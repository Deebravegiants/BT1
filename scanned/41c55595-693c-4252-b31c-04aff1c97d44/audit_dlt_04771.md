# [H] Users can exchange tokens to ETH or other ERC777 tokens without paying `exchangeFee`.

## Summary
Severity: High
Chain: Smart contract
Component: 2022-10-mover
Published: 2022-10-28
Source: https://github.com/sherlock-audit/2022-10-mover-judging/issues/115
Type: sherlock-finding

## Details
hansfriese

high

# Users can exchange tokens to ETH or other ERC777 tokens without paying `exchangeFee`.

## Summary
Users can exchange tokens to ETH or other ERC777 tokens without paying `exchangeFee`.

## Vulnerability Detail
Currently, users can exchange any tokens to `cardTopupToken` using `ExchangeProxy.executeSwapDirect()` and they should pay the `exchangeFee`.

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

_Trimmed to 38 lines — full report: https://github.com/sherlock-audit/2022-10-mover-judging/issues/115_
