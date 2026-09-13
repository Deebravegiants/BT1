# [M] THORChain incident: The THORChain network of the cross-chain DeFi protocol was interrupted. The official said that the consensus problem has been iden

## Summary
Severity: Medium
Target: THORChain
Loss: -
Attack method: Network interruption
Published: 2022-10-28
Source: https://twitter.com/THORChain/status/1585800482764730369
Type: slowmist-incident

## Details
The THORChain network of the cross-chain DeFi protocol was interrupted. The official said that the consensus problem has been identified and a patch will be released. The code pushes cosmos.Uint (instead of uint64) into the string, which causes the string to get an arbitrarily large integer instead of the actual value, causing the memo string to be on a different node. On October 28th, THORChain was back online and produced blocks. The network is signing block transactions, so pending transactions should start going through. Once the queue is cleared, the transaction will be re-enabled. Expect 2-3 hours. During the network outage, investors did not lose any funds. However, the exchange deposits and withdrawals of Thorchain's native currency RUNE have been suspended on centralized exchanges such as Kucoin.
