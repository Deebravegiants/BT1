# [M] Bitfinex incident: The non-custodial exchange DeversiFi released a post-mortem analysis report for the previous gas transaction that included 7676.62

## Summary
Severity: Medium
Target: Bitfinex
Loss: 50.62 ETH
Attack method: Handle inventory defects with fixed precision and extended value range
Published: 2021-09-27
Source: https://blog.deversifi.com/23-7-million-dollar-ethereum-transaction-fee-post-mortem/
Type: slowmist-incident

## Details
The non-custodial exchange DeversiFi released a post-mortem analysis report for the previous gas transaction that included 7676.62 ETH, saying that the potential problems in the EthereumJS library are combined with the gas fee changes related to the EIP-1559 upgrade in some cases, and the Ledger hardware wallet may exist The display problem of, may lead to extremely high transaction fees. When this happens, only wallets with very large funds will be affected, and other users will display transaction failures during transactions. In addition, after Bitfinex negotiated with the miners, the miners had returned 7,626 ETH, and the remaining 50 ETH was provided to the miners as a refund fee. It was previously reported that a major wallet on the Bitfinex exchange made a $100,000 USDT transfer with a total of 7676.62 ETH (approximately US$23.54 million) in Gas fees. The final recipient was a non-custodial spin-off from Bitfinex in 2019. Exchange DeversiFi.
