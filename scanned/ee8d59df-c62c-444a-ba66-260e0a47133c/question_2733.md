# Q2733: DepositOnChainUtxos: stamp UTXOs with circomData.timeStamp +  [when a hook mutates state betw]

## Question
Can an unprivileged attacker invoke the DepositOnChainUtxos action and stamp UTXOs with circomData.timeStamp + utxoIndex colliding with an existing commitment, where the collided leaf becomes unspendable while a duplicate nullifier looms, to pull a victim's approved tokens or mint on-chain UTXOs without backing, specifically when a hook mutates state between the check and the write (where the check-to-write gap is widened)?

## Target
- File/function: contracts/external-actions/DepositOnChainUtxosExternalAction.sol :: runAction / countUtxos
- Entrypoint: Hinkal.transact (DepositOnChainUtxos action)
- Attacker controls: originalSender, externalActionMetadata (utxoAmounts), erc20TokenAddresses, timeStamp
- Exploit idea: consume allowance of a non-submitter or mint UTXOs with no transfer
- Invariant to test: `from` of every transferFrom == msg.sender of the transact carrying the proof
- Expected Immunefi impact: Critical: direct theft of shielded or in-flight user funds
- Fast validation: Foundry: victim approves action, attacker submits proof, assert victim funds pulled
