# [M] Bridging without any swap ops is fee free in

## Summary
Severity: Medium
Contest weight: 0.5809
Dataset id: 22795
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Bridging without any swap ops is fee free in Maradona When we only have a bridge op in Maradona::takeTokensAndTrade, computableFeeAmount is zero since swapOps.length == 0.
```solidity
uint256 computableFeeAmount = 0;
for(uint256 i = 0; i < swapOps.length; i++ ){
    OperationParameters memory op = swapOps[i];
    if(op.useContractFunds) {
        break;
    }
    computableFeeAmount += op.amountIn;
}
```
Consequently, attempting to charge a fee the first time will succeed since the fee amounts will be zero (the fee amounts charged are the adjusted variables in the
```solidity
uint256 txFeeBps = feePerUserTrade[msg.sender].isSet ? feePerUserTrade[msg.sender].fee : minDefaultFeeUser;
uint256 minTerraceFeeBps = feePerUserTerrace[msg.sender].isSet ? feePerUserTerrace[msg.sender].fee : minDefaultFeeTerrace;
uint256 feeValueForFeeReceiver = (amount * feeRateBps) / 10000;
uint256 feeValueForTerrace = (feeValueForFeeReceiver * txFeeBps) / 10000;
uint256 minFeeValueForTerrace = (amount * minTerraceFeeBps) / 10000;
uint256 adjustedFeeValueForTerrace = feeValueForTerrace > minFeeValueForTerrace ? feeValueForTerrace : minFeeValueForTerrace;
uint256 adjustedFeeValueForFeeReceiver = feeValueForTerrace > minFeeValueForTerrace ? feeValueForFeeReceiver - feeValueForTerrace : feeValueForFeeReceiver;
```
No fee is transferred out since the fee amounts are zero and the second attempt to charging fees is skipped since the first attempt already succeeded.
```solidity
if (!succeeded) {
    (succeeded, ) = tryToChargeFees(
```
Protocol loses expected fees from use of its contracts.

## Recommendation
Only attempt to charge fees the first time if swap ops exist. When calculating the amount to charge fees on the second time, if only bridging, calculate based on the contract balance (subtracting the bridge fee if bridging ETH).
