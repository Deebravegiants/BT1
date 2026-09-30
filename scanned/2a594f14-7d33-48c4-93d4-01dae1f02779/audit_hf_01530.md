# [M] M-1 Centralization risks

## Summary
Severity: Medium
Contest weight: 0.0935
Dataset id: 8155
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The smart contract system of the bridge exhibits signiﬁcant centralization and lack of trustlessness. The
owner has the authority to change the implementation of both the FireBridge and FToken contracts.
Minting of FBTC on the EVM chains, cross-chain EVM transfers, and spending the BTC locked at the
Bitcoin-EVM bridge are also centralized.
Additionally, the owner can set unlimited fees, as the FeeConfig.minFee parameter is not capped.

## Recommendation
While centralization and trustfulness may be intended by design, it is recommended to implement
constraints to cap the minFee parameter to prevent the setting of unlimited fees. This can help mitigate
risks associated with excessive centralization and enhance the trustworthiness of the system.
Additionally, we recommend improving the validation infrastructure to bring more decentralization to the
minting and spending process.
