# [M] externalSwap() No check msg.value when _ETH_ADDRESS_

## Summary
Severity: Medium
Reporter: bin2chen
Source: https://github.com/sherlock-audit/2022-11-dodo/blob/main/contracts/SmartRoute/DODORouteProxy.sol#L179-L194
Type: audit-issue

## Details
# externalSwap() No check msg.value when _ETH_ADDRESS_

## Summary
DODORouteProxy#externalSwap() when token=_ETH_ADDRESS_, no check if the “fromTokenAmount“ is equal to msg.value
If there is leftover eth in the contract, you can use it directly without actually passing msg.value

## Vulnerability Detail
only claimTokens when check != _ETH_ADDRESS_

```solidity
    function externalSwap(
        address fromToken,
        address toToken,
        address approveTarget,
        address swapTarget,
        uint256 fromTokenAmount,
        uint256 minReturnAmount,
        bytes memory feeData,
        bytes memory callDataConcat,
        uint256 deadLine
    ) external payable judgeExpired(deadLine) returns (uint256 receiveAmount) {      
...

        // transfer in fromToken
        if (fromToken != _ETH_ADDRESS_) {
.....
            IDODOApproveProxy(_DODO_APPROVE_PROXY_).claimTokens(
                fromToken,
                msg.sender,
                address(this),
                fromTokenAmount   //****@audit fromToken != _ETH_ADDRESS_ is ok ***/
            );
        }
.....      
      
            //***@audit use "fromTokenAmount" without check msg.value == fromTokenAmount  when fromToken == _ETH_ADDRESS_****/
            (bool success, bytes memory result) = swapTarget.call{
                value: fromToken == _ETH_ADDRESS_ ? fromTokenAmount : 0 
            }(callDataConcat);
```


## Impact

If there is leftover eth in the contract, you can use it directly without actually passing msg.value

## Code Snippet

https://github.com/sherlock-audit/2022-11-dodo/blob/main/contracts/SmartRoute/DODORouteProxy.sol#L179-L194

## Tool used

Manual Review

## Recommendation

```solidity
    function externalSwap(
        address fromToken,
        address toToken,
        address approveTarget,
        address swapTarget,
        uint256 fromTokenAmount,
        uint256 minReturnAmount,
        bytes memory feeData,
        bytes memory callDataConcat,
        uint256 deadLine
    ) external payable judgeExpired(deadLine) returns (uint256 receiveAmount) {      
...

        // transfer in fromToken
        if (fromToken != _ETH_ADDRESS_) {
.....
            IDODOApproveProxy(_DODO_APPROVE_PROXY_).claimTokens(
                fromToken,
                msg.sender,
                address(this),
                fromTokenAmount
            );
-       }
+       } else {
+            require(msg.value == fromTokenAmount,"ETH_VALUE_WRONG");
+        }
}
```
