# Q3033: DepositOnChainUtxos: require deltaAmounts[i]==0 while amountC [when the token is a fee-on-tra]

## Question
Can an unprivileged attacker invoke the DepositOnChainUtxos action and require deltaAmounts[i]==0 while amountChanges encode a hidden non-zero via onChainCreation, where the zero-delta check is bypassed by the onChainCreation path, to pull a victim's approved tokens or mint on-chain UTXOs without backing, specifically when the token is a fee-on-transfer token (where delivered amount is below the stated amount)?

## Target
- File/function: contracts/external-actions/DepositOnChainUtxosExternalAction.sol :: runAction / countUtxos
- Entrypoint: Hinkal.transact (DepositOnChainUtxos action)
- Attacker controls: originalSender, externalActionMetadata (utxoAmounts), erc20TokenAddresses, timeStamp
- Exploit idea: consume allowance of a non-submitter or mint UTXOs with no transfer
- Invariant to test: `from` of every transferFrom == msg.sender of the transact carrying the proof
- Expected Immunefi impact: Critical: direct theft of shielded or in-flight user funds
- Fast validation: Foundry: victim approves action, attacker submits proof, assert victim funds pulled
