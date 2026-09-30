# [H] THORChain incident: The decentralized cross-chain transaction protocol THORChain (RUNE) updated the attack situation, claiming that the amount of lost

## Summary
Severity: High
Target: THORChain
Loss: $ 7,600,000
Attack method: False top-up
Published: 2021-07-16
Source: https://twitter.com/THORChain/status/1415813696857591813
Type: slowmist-incident

## Details
The decentralized cross-chain transaction protocol THORChain (RUNE) updated the attack situation, claiming that the amount of lost assets was about 4000 ETH. The initial assessment is that the attack was a logical vulnerability when Eth Bifrost used the routing contract to capture ERC-20 tokens. The attacker use. Not long ago, THORChain updated Eth Bifrost to allow the routing contract to be "encapsulated" by the contract. The attacker uses this to send a transaction with msg.value = 200 ETH and immediately uses the contract to transfer it back to itself, while Bifrost will report msg. value = 200 instead of depositAmount = 0, so as to realize the profit of calling the routing contract with the amount of 0 ETH.
