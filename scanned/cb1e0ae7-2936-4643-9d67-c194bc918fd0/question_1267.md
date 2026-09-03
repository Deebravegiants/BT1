# Q1267: residual value in DepositOnChainUtxosExternalAction: approveUnlimited left a standing al [when the ETH (address(0)) leg ]

## Question
In a DepositOnChainUtxos external action, given that approveUnlimited left a standing allowance from the action to the router, can an unprivileged attacker construct the next transaction so that value the protocol parked in the action is pulled out as their own output UTXO or to their address, beyond the -deltaAmountChanges Hinkal sent it, specifically when the ETH (address(0)) leg is present alongside (where the msg.value branch adds a second accounting path)?

## Target
- File/function: contracts/external-actions/DepositOnChainUtxosExternalAction.sol :: DepositOnChainUtxosExternalAction.runAction
- Entrypoint: Hinkal.transact
- Attacker controls: externalActionMetadata, erc20TokenAddresses ordering, deltaAmountChanges via amountChanges
- Exploit idea: claim pre-existing/refunded/stranded action balance via handleOut or router approval
- Invariant to test: tokens leaving an action in a tx == -deltaAmountChanges Hinkal sent it that tx
- Expected Immunefi impact: Critical: direct theft of shielded or in-flight user funds
- Fast validation: Foundry: seed the residual, run the action, assert attacker captures it
