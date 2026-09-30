# [M] M-14 | Traders Can’t Close Position Pre Settlement

## Summary
Severity: Medium
Contest weight: 0.0887
Dataset id: 22070
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Traders may encounter difficulties in closing positions and, to a lesser extent, modifying positions. But of utmost significance, traders may find themselves unable to close their positions before settlement if Liquidity Providers close their positions first. As a result, traders may not be able to realize profit based on the current pool price and may have to wait until settlement, leading to temporarily locked funds and potential loss of yield for traders who are unable to close a profitable position promptly.

## Recommendation
It is advised to document to users that the option to close trades before settlement is not guaranteed and is dependent on the availability of liquidity.
