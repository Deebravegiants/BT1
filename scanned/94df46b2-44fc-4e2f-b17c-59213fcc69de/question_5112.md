# Q5112: residual value in DepositOnChainUtxosExternalAction: stranded relay fees sit in the acti [when routed through HinkalWrap]

## Question
In a DepositOnChainUtxos external action, given that stranded relay fees sit in the action because circomData.relay was address(0), can an unprivileged attacker construct the next transaction so that value the protocol parked in the action is pulled out as their own output UTXO or to their address, beyond the -deltaAmountChanges Hinkal sent it, specifically when routed through HinkalWrapper's fee settlement first (where an extra value hop precedes Hinkal)?

## Target
- File/function: contracts/external-actions/DepositOnChainUtxosExternalAction.sol :: DepositOnChainUtxosExternalAction.runAction
- Entrypoint: Hinkal.transact
- Attacker controls: externalActionMetadata, erc20TokenAddresses ordering, deltaAmountChanges via amountChanges
- Exploit idea: claim pre-existing/refunded/stranded action balance via handleOut or router approval
- Invariant to test: tokens leaving an action in a tx == -deltaAmountChanges Hinkal sent it that tx
- Expected Immunefi impact: Critical: direct theft of shielded or in-flight user funds
- Fast validation: Foundry: seed the residual, run the action, assert attacker captures it
