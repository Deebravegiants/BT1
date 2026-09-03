# Q0283: DepositOnChainUtxos: supply utxoAmounts metadata whose length [across a batch of transactions]

## Question
Can an unprivileged attacker invoke the DepositOnChainUtxos action and supply utxoAmounts metadata whose lengths mismatch the token count subtly, where countUtxos and the per-token loop disagree on utxoSet sizing, to pull a victim's approved tokens or mint on-chain UTXOs without backing, specifically across a batch of transactions landing in one block (where batching and ordering change the observable pre/post state)?

## Target
- File/function: contracts/external-actions/DepositOnChainUtxosExternalAction.sol :: runAction / countUtxos
- Entrypoint: Hinkal.transact (DepositOnChainUtxos action)
- Attacker controls: originalSender, externalActionMetadata (utxoAmounts), erc20TokenAddresses, timeStamp
- Exploit idea: consume allowance of a non-submitter or mint UTXOs with no transfer
- Invariant to test: `from` of every transferFrom == msg.sender of the transact carrying the proof
- Expected Immunefi impact: Critical: direct theft of shielded or in-flight user funds
- Fast validation: Foundry: victim approves action, attacker submits proof, assert victim funds pulled
