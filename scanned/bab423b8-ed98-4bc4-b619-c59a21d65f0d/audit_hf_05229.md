# [M] Insufficient fee validation in STBL_Register::setupAsset can cause underflow

## Summary
Severity: Medium
Contest weight: 0.0000
Dataset id: 23384
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The STBL_Register::setupAsset and STBL_Register::setFees functions validate individual fees but ignore their cumulative impact. Consider the following logic in STBL_MetadataLib.calculateDepositFees where the depositfeeAmount, haircutAmount and insurancefeeAmount are calculated on the gross stable value:
```solidity
function calculateDepositFees(YLD_Metadata memory data) internal pure returns (YLD_Metadata memory) {
    // All deposit-time fees calculated on same base (stableValueGross)
    data.depositfeeAmount = (data.stableValueGross * data.Fees.depositFee) / 10000;
    data.haircutAmount = (data.stableValueGross * data.Fees.hairCut) / 10000;
    data.insurancefeeAmount = (data.stableValueGross * data.Fees.insuranceFee) / 10000;
    data.withdrawfeeAmount = (data.stableValueGross * data.Fees.withdrawFee) / 10000;
    return data; //@audit depositfeeAmount, haircutAmount and insurancefeeAmount are calculated on
    stableValueGross,!
}
```
Both the STBL_LT1_Issuer and STBL_PT1_Issuer contracts calculate the net stable value as follows:
```
MetaData.stableValueNet = (MetaData.stableValueGross -
(MetaData.depositfeeAmount +
MetaData.haircutAmount +
MetaData.insurancefeeAmount));
```
This would mean that if the sum of all fees in basis points exceeds 10000, the metadata logic will always revert when computing the net stable value.
Impact: A combination of fees where the sum of deposit fee, hair cut and insurance fee exceeds 10000 can cause underflow in net stable value calculation.

## Recommendation
Consider introducing a cumulative check in the STBL_Register::setupAsset and STBL_Register::setFees functions.
