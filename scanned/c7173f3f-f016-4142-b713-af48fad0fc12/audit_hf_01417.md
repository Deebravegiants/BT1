# [C] C-1 Inﬂation attack on iToken

## Summary
Severity: Critical
Contest weight: 0.1412
Dataset id: 7308
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Until iToken has sufﬁcient totalSupply, an attacker can manipulate the underlying/iToken exchange rate by directly transferring the underlying asset to the iToken smart contract. This leads to rounding issues in mint and redeemUnderlying causing a user to lose some amount of their underlying assets. Due to the possibility of permanent loss of user assets, such issues have a critical severity rating.

## Recommendation
Although this issue can be hotﬁxed through accurate deployment procedures and conﬁguration settings, we recommend ﬁxing it at the smart contract code level either by preventing the iToken from having a nonzero but small totalSupply or by ensuring accurate accounting of the underlying asset in the smart contract.
