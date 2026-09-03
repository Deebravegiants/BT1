# Q3516: msg.value double-count in an Emporium external action [when the attacker sandwiches t]

## Question
Can an unprivileged attacker in an Emporium external action send msg.value larger than amountChanges for the ETH leg and reclaim the surplus as a UTXO, so the address(0) branch `balanceDif = new + msg.value - old` credits the same ETH to two accounting terms and mints unbacked shielded ETH, specifically when the attacker sandwiches the tx with their own deposit and withdraw (where surrounding state is attacker-tuned)?

## Target
- File/function: contracts/Hinkal.sol :: transact / EmporiumUpgradeable.runAction
- Entrypoint: Hinkal.transact
- Attacker controls: msg.value, erc20TokenAddresses containing address(0), amountChanges, onChainCreation
- Exploit idea: make the ETH balance delta serve both the amountChanges term and a UTXO term
- Invariant to test: msg.value backing == exactly one accounting term in the balance equation
- Expected Immunefi impact: Critical: minting shielded value without backing (protocol insolvency)
- Fast validation: Foundry: send ETH, assert minted ETH UTXO value exceeds address(this).balance delta
