# Q3392: slippage floor abuse: set slippageValues[i] negative so the re [when the attacker sandwiches t]

## Question
Can an unprivileged attacker set slippageValues[i] negative so the require balanceDif >= slippageValues[i] passes on a loss, so Hinkal.transact's `balanceDif >= circomData.slippageValues[i]` check accepts a transaction where the vault loses value relative to the shielded amounts, since slippageValues sign is attacker-chosen, specifically when the attacker sandwiches the tx with their own deposit and withdraw (where surrounding state is attacker-tuned)?

## Target
- File/function: contracts/Hinkal.sol :: transact (slippage require)
- Entrypoint: Hinkal.transact
- Attacker controls: slippageValues, amountChanges, external action output
- Exploit idea: use a permissive/negative slippage floor to accept value loss
- Invariant to test: slippageValues encode a genuine minimum received, not an attacker escape hatch
- Expected Immunefi impact: Critical: direct theft of shielded or in-flight user funds
- Fast validation: Foundry: set negative slippage, run a lossy action, assert vault shortfall accepted
