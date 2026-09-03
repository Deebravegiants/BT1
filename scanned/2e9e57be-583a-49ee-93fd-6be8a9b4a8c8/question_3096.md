# Q3096: residual value in DepositOnChainUtxosExternalAction: the action received -delta for a to [when the token is a fee-on-tra]

## Question
In a DepositOnChainUtxos external action, given that the action received -delta for a token the caller then omits from the output UTXO set, can an unprivileged attacker construct the next transaction so that value the protocol parked in the action is pulled out as their own output UTXO or to their address, beyond the -deltaAmountChanges Hinkal sent it, specifically when the token is a fee-on-transfer token (where delivered amount is below the stated amount)?

## Target
- File/function: contracts/external-actions/DepositOnChainUtxosExternalAction.sol :: DepositOnChainUtxosExternalAction.runAction
- Entrypoint: Hinkal.transact
- Attacker controls: externalActionMetadata, erc20TokenAddresses ordering, deltaAmountChanges via amountChanges
- Exploit idea: claim pre-existing/refunded/stranded action balance via handleOut or router approval
- Invariant to test: tokens leaving an action in a tx == -deltaAmountChanges Hinkal sent it that tx
- Expected Immunefi impact: Critical: direct theft of shielded or in-flight user funds
- Fast validation: Foundry: seed the residual, run the action, assert attacker captures it
