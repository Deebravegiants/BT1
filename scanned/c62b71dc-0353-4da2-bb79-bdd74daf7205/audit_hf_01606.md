# [M] TAX-4 | Centralization Risk

## Summary
Severity: Medium
Contest weight: 0.0819
Dataset id: 8632
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The operator address is not a multi-sig and has potentially dangerous permissions for disableAutoCalculateTax, enableAutoCalculateTax, excludeAddressFromTax, includeAddressInTax, setBurnThreshold, setTaxCollectorAddress, setTaxExclusionForAddress, setTaxRate, setTaxTiersRate, setTaxTiersTwap, setTaxableHamsterOracle, transferTaxOffice. Most notably transferTaxOffice sets the taxOffice for the hamster contract, potentially compromising the hamster taxOffice permissioned functions as well.

## Recommendation
Make the operator a multi-sig and/or introduce a timelock for the community to monitor events.
