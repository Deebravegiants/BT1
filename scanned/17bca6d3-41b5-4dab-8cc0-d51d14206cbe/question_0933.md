# Q0933: DepositOnChainUtxos: stamp UTXOs with circomData.timeStamp +  [under a token with 6 decimals]

## Question
Can an unprivileged attacker invoke the DepositOnChainUtxos action and stamp UTXOs with circomData.timeStamp + utxoIndex colliding with an existing commitment, where the collided leaf becomes unspendable while a duplicate nullifier looms, to pull a victim's approved tokens or mint on-chain UTXOs without backing, specifically under a token with 6 decimals (where decimal scaling shifts the accounting boundary)?

## Target
- File/function: contracts/external-actions/DepositOnChainUtxosExternalAction.sol :: runAction / countUtxos
- Entrypoint: Hinkal.transact (DepositOnChainUtxos action)
- Attacker controls: originalSender, externalActionMetadata (utxoAmounts), erc20TokenAddresses, timeStamp
- Exploit idea: consume allowance of a non-submitter or mint UTXOs with no transfer
- Invariant to test: `from` of every transferFrom == msg.sender of the transact carrying the proof
- Expected Immunefi impact: Critical: direct theft of shielded or in-flight user funds
- Fast validation: Foundry: victim approves action, attacker submits proof, assert victim funds pulled
