# [M] Loss of surplus Eth

## Summary
Severity: Medium
Chain: Smart contract
Component: 2022-10-mover
Published: 2022-10-28
Source: https://github.com/sherlock-audit/2022-10-mover-judging/issues/82
Type: sherlock-finding

## Details
sorrynotsorry

medium

# Loss of surplus Eth

## Summary
The ExchangeProxy contract accepts native token as Ether. In executeSwapDirect() function, it's compared whether the msg.value is equal or greater than the submitted `_amount` for the swap. But if the user sends more Eth than the submitted `_amount`, it remains in the contract.
## Vulnerability Detail
The extra sent Eth remains in the contract and it's not refunded back even after a successful swap. There is `emergencyTransfer` function to send back the funds to the users who inadvertently sends their funds to the contract, however, this does not comply the urgent needs of the user which is having the remainder of the sent funds.
Even it's returned back by the admin after some time, the user will have disadvantage of it if in a bear market condition like we're in now.

## Impact
Loss of funds, financial lose of funds.
## Code Snippet
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
```

_Trimmed to 38 lines — full report: https://github.com/sherlock-audit/2022-10-mover-judging/issues/82_
