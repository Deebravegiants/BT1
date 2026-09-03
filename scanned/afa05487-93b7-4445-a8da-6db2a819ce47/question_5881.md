# Q5881: residual value in ExternalActionSwap: the action already holds a dust bal [when the cited root is many ba]

## Question
In a LiFi swap external action, given that the action already holds a dust balance of the output token from a prior tx, can an unprivileged attacker construct the next transaction so that value the protocol parked in the action is pulled out as their own output UTXO or to their address, beyond the -deltaAmountChanges Hinkal sent it, specifically when the cited root is many batches old (where a stale historical root is used for inclusion)?

## Target
- File/function: contracts/external-actions/swaps/ExternalActionSwap.sol :: ExternalActionSwap.swap
- Entrypoint: Hinkal.transact
- Attacker controls: externalActionMetadata, erc20TokenAddresses ordering, deltaAmountChanges via amountChanges
- Exploit idea: claim pre-existing/refunded/stranded action balance via handleOut or router approval
- Invariant to test: tokens leaving an action in a tx == -deltaAmountChanges Hinkal sent it that tx
- Expected Immunefi impact: Critical: direct theft of shielded or in-flight user funds
- Fast validation: Foundry: seed the residual, run the action, assert attacker captures it
