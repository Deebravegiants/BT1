# Q4958: DepositOnChainUtxos: set originalSender to a victim who grant [when routed through HinkalWrap]

## Question
Can an unprivileged attacker invoke the DepositOnChainUtxos action and set originalSender to a victim who granted the action a standing allowance, where transferERC20TokenFrom pulls from originalSender, not the proof submitter, to pull a victim's approved tokens or mint on-chain UTXOs without backing, specifically when routed through HinkalWrapper's fee settlement first (where an extra value hop precedes Hinkal)?

## Target
- File/function: contracts/external-actions/DepositOnChainUtxosExternalAction.sol :: runAction / countUtxos
- Entrypoint: Hinkal.transact (DepositOnChainUtxos action)
- Attacker controls: originalSender, externalActionMetadata (utxoAmounts), erc20TokenAddresses, timeStamp
- Exploit idea: consume allowance of a non-submitter or mint UTXOs with no transfer
- Invariant to test: `from` of every transferFrom == msg.sender of the transact carrying the proof
- Expected Immunefi impact: Critical: direct theft of shielded or in-flight user funds
- Fast validation: Foundry: victim approves action, attacker submits proof, assert victim funds pulled
