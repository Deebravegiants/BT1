# [C] C-01 | Incorrect Price From aspTKN Oracle

## Summary
Severity: Critical
Contest weight: 0.1445
Dataset id: 22154
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The getPrice function should return price as (aspTKN / pairedLPToken) which is consumed by the Fraxlend isSolvent function to determine a borrower's LTV. However, the calculation is incorrect because it takes price from the spTKN oracle and divides it by _aspTknPerSpTkn when it should be multiplying instead. Therefore, the price returned is always incorrect and borrower's LTV is miscalculated in Fraxlend.

## Recommendation
Instead of `_priceLow = (_priceLow * _assetFactor) / _aspTknPerSpTkn;` do `_priceLow = (_priceLow * _aspTknPerSpTkn) / _assetFactor;`
