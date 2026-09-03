# Q3971: residual value in EmporiumUpgradeable: a prior Emporium op set a persisten [when amountChanges[i] is exact]

## Question
In an Emporium external action, given that a prior Emporium op set a persistent approval on the action's behalf, can an unprivileged attacker construct the next transaction so that value the protocol parked in the action is pulled out as their own output UTXO or to their address, beyond the -deltaAmountChanges Hinkal sent it, specifically when amountChanges[i] is exactly zero for the affected token (where the zero branch skips value movement)?

## Target
- File/function: contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol :: EmporiumUpgradeable.runAction
- Entrypoint: Hinkal.transact
- Attacker controls: externalActionMetadata, erc20TokenAddresses ordering, deltaAmountChanges via amountChanges
- Exploit idea: claim pre-existing/refunded/stranded action balance via handleOut or router approval
- Invariant to test: tokens leaving an action in a tx == -deltaAmountChanges Hinkal sent it that tx
- Expected Immunefi impact: Critical: direct theft of shielded or in-flight user funds
- Fast validation: Foundry: seed the residual, run the action, assert attacker captures it
