# Q3106: msg.value double-count in a prooflessDeposit call [when the token is a fee-on-tra]

## Question
Can an unprivileged attacker in a prooflessDeposit call send msg.value while onChainCreation[i] is true for the ETH leg zeroing the RHS, so the address(0) branch `balanceDif = new + msg.value - old` credits the same ETH to two accounting terms and mints unbacked shielded ETH, specifically when the token is a fee-on-transfer token (where delivered amount is below the stated amount)?

## Target
- File/function: contracts/Hinkal.sol :: transact / Hinkal.prooflessDeposit
- Entrypoint: Hinkal.transact
- Attacker controls: msg.value, erc20TokenAddresses containing address(0), amountChanges, onChainCreation
- Exploit idea: make the ETH balance delta serve both the amountChanges term and a UTXO term
- Invariant to test: msg.value backing == exactly one accounting term in the balance equation
- Expected Immunefi impact: Critical: minting shielded value without backing (protocol insolvency)
- Fast validation: Foundry: send ETH, assert minted ETH UTXO value exceeds address(this).balance delta
