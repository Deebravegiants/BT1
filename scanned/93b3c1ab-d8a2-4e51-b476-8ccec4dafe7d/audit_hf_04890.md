# [M] tryToChargeForGas() return gasAmountCharged

## Summary
Severity: Medium
Contest weight: 0.6932
Dataset id: 22806
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
in tryToChargeForGas() if needToBringTokens==false and feesTokenAddress==address(0) It doesn't set the return value gasAmountCharged, it always returns 0.
The tryToChargeForGas() code is as follows
```solidity
function tryToChargeForGas(
    ...
    // this means that the fee token is not the output token of the last swapOp
    if (needToBringTokens){
        require(feesTokenAddress != address(0), "Messi: feesTokenAddress must not be 0x0 if eth is not the output");
        IERC20 feesToken = IERC20(feesTokenAddress);
        uint256 balance = feesToken.balanceOf(receivingUser);
        if (balance > feeValue) {
            feesToken.safeTransferFrom(receivingUser, feeCollector, feeValue);
            succeeded = true;
            amount = feeValue;
            emit GasCharged(receivingUser, feeValue, feesTokenAddress, gasAmount, gasToFeeTokenExchangeRate);
        } else if (mandatory){
            revert("Messi: cannot charge for gas bringing tokens");
        }
    } else { // this means that the fee token is the output token of the last swapOp
        if (feesTokenAddress != address(0)) {
            IERC20 feesToken = IERC20(feesTokenAddress);
            uint256 balance = feesToken.balanceOf(address(this));
            if (balance > feeValue) {
                feesToken.safeTransfer(feeCollector, feeValue);
                succeeded = true;
                amount = feeValue;
                emit GasCharged(receivingUser, feeValue, feesTokenAddress, gasAmount, gasToFeeTokenExchangeRate);
            } else if (mandatory) {
                revert("Messi: cannot charge for gas with tokens in contract");
            }
        } else {
            require(address(this).balance >= feeValue, "Messi: not enough eth to charge for gas");
            payable(feeCollector).transfer(feeValue);
            succeeded = true;
            emit GasCharged(receivingUser, feeValue, feesTokenAddress, gasAmount, gasToFeeTokenExchangeRate);
        }
    }
}
```
From the above code we know that if needToBringTokens==false and feesTokenAddress==address(0) does not set the return value gasAmountCharged and always returns 0.
An incorrect gasAmountCharged will result in an incorrect bridgeOp.amountIn:
bridgeOp.amountIn -= gasAmountCharged
```solidity
function takeTokensAndTrade(
    ...
    // We charge for gas and fees
    if (!gasCharged) {
        (gasCharged, gasAmountCharged) = tryToChargeForGas(
            (initialGas - gasleft()) * tx.gasprice + valueToSend,
            gasToFeeTokenExchangeRate,
            feesTokenAddress,
            receivingUser,
            true,
            gasCharged,
            // If there is a brige, we check if the input of the bridge is the fee token
            // Otherwise, we check if the output of the last swapOp is the fee token
            // Because if so, we dont need to bring the tokens to the contract
            bridgeFound? bridgeOp.inputToken != feesTokenAddress: swapOps.length > 0? swapOps[swapOps.length - 1].outputToken != feesTokenAddress: claimOp.outputToken != feesTokenAddress
        );
    }
}
```
else {
```solidity
    if (bridgeOp.inputToken == feesTokenAddress) {
        bridgeOp.amountIn = bridgeOp.amountIn - gasAmountCharged;
    }
    if (!inputFeeCharged) {
        bridgeOp.amountIn = bridgeOp.amountIn - feesDeductedFinal;
    }
    if (bridgeOp.inputToken != address(0)) {
        IERC20 tokenToBridge = IERC20(bridgeOp.inputToken);
        tokenToBridge.approve(markets[bridgeOp.exchangeID], bridgeOp.amountIn);
    } else {
        valueToSend = valueToSend;
    }
    bridge(bridgeOp, bridgeFeeEth + valueToSend);
}
// End of (4)
```
Wrong gasAmountCharged will cause bridgeOp.amountIn to be wrong Unable to execute takeTokensAndTrade() properly

## Recommendation
```solidity
function tryToChargeForGas(
    ...
    } else {
        require(address(this).balance >= feeValue, "Messi: not enough eth to charge for gas");
        payable(feeCollector).transfer(feeValue);
        succeeded = true;
        amount = feeValue;
        emit GasCharged(receivingUser, feeValue, feesTokenAddress, gasAmount, gasToFeeTokenExchangeRate);
    }
}
```
