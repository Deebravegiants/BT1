# Q5814: msg.value double-count in a HinkalWrapper.prooflessDeposit call [when the tree has exactly one ]

## Question
Can an unprivileged attacker in a HinkalWrapper.prooflessDeposit call list address(0) plus WETH and unwrap mid-call so ETH satisfies two legs, so the address(0) branch `balanceDif = new + msg.value - old` credits the same ETH to two accounting terms and mints unbacked shielded ETH, specifically when the tree has exactly one prior leaf (where roots[MINIMUM_INDEX] equals that leaf directly)?

## Target
- File/function: contracts/Hinkal.sol :: transact / HinkalWrapper.prooflessDeposit
- Entrypoint: Hinkal.transact
- Attacker controls: msg.value, erc20TokenAddresses containing address(0), amountChanges, onChainCreation
- Exploit idea: make the ETH balance delta serve both the amountChanges term and a UTXO term
- Invariant to test: msg.value backing == exactly one accounting term in the balance equation
- Expected Immunefi impact: Critical: minting shielded value without backing (protocol insolvency)
- Fast validation: Foundry: send ETH, assert minted ETH UTXO value exceeds address(this).balance delta
