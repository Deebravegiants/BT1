# Q4783: DepositOnChainUtxos: supply utxoAmounts metadata whose length [when the deposit uses proofles]

## Question
Can an unprivileged attacker invoke the DepositOnChainUtxos action and supply utxoAmounts metadata whose lengths mismatch the token count subtly, where countUtxos and the per-token loop disagree on utxoSet sizing, to pull a victim's approved tokens or mint on-chain UTXOs without backing, specifically when the deposit uses prooflessDeposit instead of a proof (where the no-proof mint path is taken)?

## Target
- File/function: contracts/external-actions/DepositOnChainUtxosExternalAction.sol :: runAction / countUtxos
- Entrypoint: Hinkal.transact (DepositOnChainUtxos action)
- Attacker controls: originalSender, externalActionMetadata (utxoAmounts), erc20TokenAddresses, timeStamp
- Exploit idea: consume allowance of a non-submitter or mint UTXOs with no transfer
- Invariant to test: `from` of every transferFrom == msg.sender of the transact carrying the proof
- Expected Immunefi impact: Critical: direct theft of shielded or in-flight user funds
- Fast validation: Foundry: victim approves action, attacker submits proof, assert victim funds pulled
