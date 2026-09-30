# [M] MKTF-1 | Malicious Backing Token

## Summary
Severity: Medium
Contest weight: 0.0735
Dataset id: 17884
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In the future, GMX hopes to enable permissionless MarketToken creation. However, a MarketToken can use an arbitrary malicious backing token that performs mischievous actions such as cancelling orders on the exchange during execution when the token is transferred. Additionally, it is possible for contracts of the existing tokens on the exchange to be upgraded with new logic that is able to maliciously exploit the exchange.

## Recommendation
Be wary of malicious tokens and ensure there is no way to re-enter into the application during token transfers.
