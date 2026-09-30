# [M] When the amount of token acquired by a flash

## Summary
Severity: Medium
Contest weight: 0.5941
Dataset id: 22624
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
When the amount of token acquired by a flash loan exceeds the expected value, the callback function will fail.
The function wagmiLeverageFlashCallback is used to handle the repayment operation after flash loan. After obtaining enough saleToken, it uses _v3SwapExact to convert the saleToken into holdToken. We know that the amount of holdTokens (holdTokenAmtIn) is proportional to the amount of saleTokens (amountToPay) obtained from flash loans. Later, the function will check the holdTokenAmtIn is no large than decodedData.holdTokenDebt.
```solidity
// Swap tokens to repay the flash loan
uint256 holdTokenAmtIn = _v3SwapExact(
    v3SwapExactParams({
        isExactInput: false,
        fee: decodedData.fee,
        tokenIn: decodedData.holdToken,
        tokenOut: decodedData.saleToken,
        amount: amountToPay
    })
);
decodedData.holdTokenDebt -= decodedData.zeroForSaleToken
    ? decodedData.amounts.amount1
    : decodedData.amounts.amount0;
// Check for strict route adherence, revert the transaction if conditions are not met
(decodedData.routes.strict && holdTokenAmtIn > decodedData.holdTokenDebt).revertError(
    ErrLib.ErrorCode.SWAP_AFTER_FLASH_LOAN_FAILED
);
```
In the function _executeCallback, the amount of token finally obtained by the user through flash loan is flashBalance, which is the balance of the contract.
```solidity
// Transfer the flashBalance to the recipient
decodedData.saleToken.safeTransfer(decodedDataExt.recipient, flashBalance);
// Invoke the WagmiLeverage callback function with updated parameters
IWagmiLeverageFlashCallback(decodedDataExt.recipient).wagmiLeverageFlashCallback(
    flashBalance,
    interest,
    decodedDataExt.originData
);
```
Now let me describe how the attacker compromises the flash loans.
First, the attacker makes a donation to the FlashLoanAggregator contract before the victim performs a flash loan (using front-run). Then victim performs a flash loan, and he/she will get much more flashBalance than expected. Finally, in the function wagmiLeverageFlashCallback, the holdTokenAmtIn is larger than expected, which leads to fail.
DOS

## Recommendation
In the function _executeCallback, the amount of token finally obtained by the user through flash loan should be the balance difference during the flash loan period.
