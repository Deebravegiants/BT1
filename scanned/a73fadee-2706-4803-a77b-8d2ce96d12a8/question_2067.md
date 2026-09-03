# Q2067: slippage floor abuse: set slippageValues to int min so any bal [when the external action retur]

## Question
Can an unprivileged attacker set slippageValues to int min so any balanceDif clears for a token you drain, so Hinkal.transact's `balanceDif >= circomData.slippageValues[i]` check accepts a transaction where the vault loses value relative to the shielded amounts, since slippageValues sign is attacker-chosen, specifically when the external action returns an empty UTXO set (where utxoAmount is zero while value still moved)?

## Target
- File/function: contracts/Hinkal.sol :: transact (slippage require)
- Entrypoint: Hinkal.transact
- Attacker controls: slippageValues, amountChanges, external action output
- Exploit idea: use a permissive/negative slippage floor to accept value loss
- Invariant to test: slippageValues encode a genuine minimum received, not an attacker escape hatch
- Expected Immunefi impact: Critical: direct theft of shielded or in-flight user funds
- Fast validation: Foundry: set negative slippage, run a lossy action, assert vault shortfall accepted
