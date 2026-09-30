# [H] H-02 | convertUSD DOS Because Of Share Rounding

## Summary
Severity: High
Contest weight: 0.2773
Dataset id: 2559
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
[LegacyMarket.convertUSD()](https://github.com/GuardianAudits/legacy-1/blob/636dc48c91b18807adf6ae71ac8eb45e22fc9ea9/markets/legacy-market/contracts/LegacyMarket.sol#L164-L167) burns synths from the converter's account and enforces a maximum difference between the actual burnt amount and the amount specified by the user to be no more than 1 unit of sUSD. However, when the [Issuer](https://github.com/Synthetixio/synthetix/blob/987f18e4f73fbfee3b984fd56934780e1df1508d/contracts/Issuer.sol#L1027-L1028) does the burning of the SDS, there is some rounding which happens on the shares. This means the end result can be with 1 unit less of a share, not sUSD. Furthermore, additional rounding can happen on [this line](https://github.com/Synthetixio/synthetix/blob/987f18e4f73fbfee3b984fd56934780e1df1508d/contracts/Issuer.sol#L300) when querying the SDS balance which will increase the margin of error. As a result, the burnt amount may deviate slightly more than 1 wei of sUSD when the debtShares ratio is above 1$ of debt per share. As the LegacyMarket does not tolerate this amount of inaccuracy, the whole transaction will revert and converting will not be possible.

## Recommendation
Consider allowing for a rounding error of 1 wei of shares rather than 1 wei of USD.
