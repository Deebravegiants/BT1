# Q3152: msg.value double-count in an internal transact (externalActionId == 0) [when the token silently return]

## Question
Can an unprivileged attacker in an internal transact (externalActionId == 0) list address(0) twice in erc20TokenAddresses so msg.value is counted once per entry, so the address(0) branch `balanceDif = new + msg.value - old` credits the same ETH to two accounting terms and mints unbacked shielded ETH, specifically when the token silently returns false on failure (where SafeERC20 and the balance delta can disagree)?

## Target
- File/function: contracts/Hinkal.sol :: transact / Hinkal._internalTransact
- Entrypoint: Hinkal.transact
- Attacker controls: msg.value, erc20TokenAddresses containing address(0), amountChanges, onChainCreation
- Exploit idea: make the ETH balance delta serve both the amountChanges term and a UTXO term
- Invariant to test: msg.value backing == exactly one accounting term in the balance equation
- Expected Immunefi impact: Critical: minting shielded value without backing (protocol insolvency)
- Fast validation: Foundry: send ETH, assert minted ETH UTXO value exceeds address(this).balance delta
