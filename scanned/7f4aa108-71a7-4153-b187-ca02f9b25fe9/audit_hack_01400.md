# [M] Synapse Protocol incident: The asset cross-chain bridge launched by the cross-chain protocol Synapse Protocol is suspected to have loopholes, and the attacke

## Summary
Severity: Medium
Target: Synapse Protocol
Loss: -
Attack method: Price Manipulation
Published: 2021-11-06
Source: https://synapseprotocol.medium.com/11-06-2021-post-mortem-of-synapse-metapool-exploit-3003b4df4ef4
Type: slowmist-incident

## Details
The asset cross-chain bridge launched by the cross-chain protocol Synapse Protocol is suspected to have loopholes, and the attacker manipulated the virtual price of nUSD Metapool, reducing it by about 12.5%. Ultimately, although the funds were withdrawn from the metapool itself, the funds were not lost. When the validator is offline, the address that took the funds from the LP tries to move the funds through the bridge, so the transaction has not yet been processed. However, the validators unanimously decided not to process this transaction because it was malicious to the LP and the entire network: as a result, ~$8.2 million in nUSD was not minted to the attacker's address on the target chain. The nUSD will be returned to the affected Avalanche LPs instead.
