# [H] since `feeData` is user supplied an attacker can  make `brokerFee=0` and pay no fees

## Summary
Severity: High
Chain: Smart contract
Component: 2022-11-dodo
Published: 2022-11-15
Source: https://github.com/sherlock-audit/2022-11-dodo-judging/issues/59
Type: sherlock-finding

## Details
simon135

high

# since `feeData` is user supplied an attacker can  make `brokerFee=0` and pay no fees

## Summary
since `feeData` is user supplied an attacker can  make `brokerFee=0` and pay no fees 
## Vulnerability Detail
since `feeData` is user supplied an attacker can  make `brokerFee=0` and pay no fees 
since there is no input validation on `brokerFeeRate` it can equal 0 and then the attacker doesn't have to pay fees.which then when making a  swap will be with no fees. 
and 
## Impact
The attacker doesn't have to pay fees 
## Code Snippet
```solidity 
        (address broker, uint256 brokerFeeRate) = abi.decode(feeData, (address, uint256));
        require(brokerFeeRate < 10**18, "DODORouteProxy: brokerFeeRate overflowed");

        uint256 routeFee = DecimalMath.mulFloor(receiveAmount, routeFeeRate);
        IERC20(toToken).universalTransfer(payable(routeFeeReceiver), routeFee);

        uint256 brokerFee = DecimalMath.mulFloor(receiveAmount, brokerFeeRate);
        IERC20(toToken).universalTransfer(payable(broker), brokerFee);
        
        receiveAmount = receiveAmount - routeFee - brokerFee;
        require(receiveAmount >= minReturnAmount, "DODORouteProxy: Return amount is not enough");
        
        if (originToToken == _ETH_ADDRESS_) {
            IWETH(_WETH_).withdraw(receiveAmount);
            payable(msg.sender).transfer(receiveAmount);
        } else {
            IERC20(toToken).universalTransfer(payable(msg.sender), receiveAmount);
        }
```
https://github.com/sherlock-audit/2022-11-dodo/blob/main/contracts/SmartRoute/DODORouteProxy.sol#L468
## Tool used


_Trimmed to 38 lines — full report: https://github.com/sherlock-audit/2022-11-dodo-judging/issues/59_
