# [M] Centralization risk in off chain oracles (particularly priceOracleSigner)

## Summary
Severity: Medium
Contest weight: 0.1861
Dataset id: 8802
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The protocol uses two off-chain oracles to (a) verify asset prices and (b) allow gasless cancellations.

Each of these off-chain signers pose a centralization risk for the protocol:
`priceOracleSigner`: This signer submits the asset prices used in the Black Scholes calculation for option value. If a malicious actor were to get control of this wallet, they could drain all the funds from every the wallet of every user with open bids by submitting high spot price values that would push the option value up.
`orderValidityOracleSigner`: This signer submits confirmation that the buyer has not gaslessly cancelled their order, and it is therefore valid to execute. If a malicious actor were to get control of this wallet, they could execute cancelled transactions, forcing buyers to buy assets they did not intend to.

Both off-chain signers have their risks, but the `orderValidityOracleSigner` seems to be accomplishing an important goal (gasless cancellations) and the downsides are limited: orders that have not yet expired can be executed within the originally defined bounds, based on the accurate asset price.

The `priceOracleSigner`, on the other hand, seems to create an undue risk for users.

## Recommendation
For `orderValidityOracleSigner`, consider whether the feature of gasless cancellations is worth the key compromise risk.

For `priceOracleSigner`, it is recommended to use a reputable, decentralized oracle such as Chainlink for such an important source of data. Unfortunately, [Chainlink's NFT Floor Price](https://docs.chain.link/data-feeds/nft-floor-price/addresses/) feeds are limited to only 10 NFTs at the moment, so I understand that this would pose a major trade-off for the protocol.
