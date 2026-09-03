# Q5114: msg.value double-count in a DepositOnChainUtxos external action [when routed through HinkalWrap]

## Question
Can an unprivileged attacker in a DepositOnChainUtxos external action list address(0) twice in erc20TokenAddresses so msg.value is counted once per entry, so the address(0) branch `balanceDif = new + msg.value - old` credits the same ETH to two accounting terms and mints unbacked shielded ETH, specifically when routed through HinkalWrapper's fee settlement first (where an extra value hop precedes Hinkal)?

## Target
- File/function: contracts/Hinkal.sol :: transact / DepositOnChainUtxosExternalAction.runAction
- Entrypoint: Hinkal.transact
- Attacker controls: msg.value, erc20TokenAddresses containing address(0), amountChanges, onChainCreation
- Exploit idea: make the ETH balance delta serve both the amountChanges term and a UTXO term
- Invariant to test: msg.value backing == exactly one accounting term in the balance equation
- Expected Immunefi impact: Critical: minting shielded value without backing (protocol insolvency)
- Fast validation: Foundry: send ETH, assert minted ETH UTXO value exceeds address(this).balance delta
