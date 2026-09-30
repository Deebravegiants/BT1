# [M] M-2 Lack of chains whitelisting

## Summary
Severity: Medium
Contest weight: 0.0719
Dataset id: 8156
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The project provides for cross-chain token transfers of FBTC through the addCrosschainRequest
function. If the network with the speciﬁed chain ID is not supported by the FBTC infrastructure, all burned
FBTC tokens in the addCrosschainRequest function will be lost.
This issue is classiﬁed as MEDIUM severity since it occurs only if the user speciﬁes an incorrect network or
if the project's website frontend misleads the user.

## Recommendation
We recommend adding a chain whitelisting in the addCrosschainRequest() function.
