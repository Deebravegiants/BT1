# [M] Bridge refunds could be lost if URBurner is not deployed at the same address on all supported chains

## Summary
Severity: Medium
Contest weight: 0.1664
Dataset id: 5146
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
ERCBurner uses relay protocol for bridging ETH from one chain to another. There is no validation of the bridgeData in swapExactInputMultiple() or relayBridge() functions: the data is passed as it is supplied by the user. Utmost care is needed to handle bridge refunds in case bridge operation fails.
According to the relay protocol docs, in some cases {notably, when the refundTo and recipient addresses are both unspecified in bridgeData}, in case of the bridge operation failing ⇒the refund will be sent to the caller address on the destination chain.
For this protocol's case, this might happen:
• URBurner is deployed at address X on Ethereum Mainnet.
• User bridges ETH to Arbitrum.
• The bridge operation fails.
• There was no refundTo address specified and no recipient address specified, so the refund will go to the caller on destination chain: which means address X on Arbitrum.
• But this address would not be the URBurner if URBurner is not deployed at the same address on all chains.
This means the refunded ETH will not be recoverable and will lead to loss of funds.

## Recommendation
If URBurner is the same address on source and destination chains, it could receive those ETH refunds and then the admin could keep track of bridge failures, rescuing and redistributing ETH to original owners. This way there would be no loss of funds.
It is recommended to try to deploy URBurner at the same address on all supported chains.
