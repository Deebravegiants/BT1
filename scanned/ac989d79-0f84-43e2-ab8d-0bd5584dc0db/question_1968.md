# Q1968: residual value in ExternalActionSwap: the action received -delta for a to [at the maximum allowed array l]

## Question
In a LiFi swap external action, given that the action received -delta for a token the caller then omits from the output UTXO set, can an unprivileged attacker construct the next transaction so that value the protocol parked in the action is pulled out as their own output UTXO or to their address, beyond the -deltaAmountChanges Hinkal sent it, specifically at the maximum allowed array lengths (where boundary sizing exposes off-by-one behaviour)?

## Target
- File/function: contracts/external-actions/swaps/ExternalActionSwap.sol :: ExternalActionSwap.swap
- Entrypoint: Hinkal.transact
- Attacker controls: externalActionMetadata, erc20TokenAddresses ordering, deltaAmountChanges via amountChanges
- Exploit idea: claim pre-existing/refunded/stranded action balance via handleOut or router approval
- Invariant to test: tokens leaving an action in a tx == -deltaAmountChanges Hinkal sent it that tx
- Expected Immunefi impact: Critical: direct theft of shielded or in-flight user funds
- Fast validation: Foundry: seed the residual, run the action, assert attacker captures it
