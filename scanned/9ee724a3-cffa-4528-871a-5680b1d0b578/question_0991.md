# Q991: Treasury withdrawal enactment can mismatch account and treasury balances in toJSONKey

## Question
Can an unprivileged attacker exercise `toJSONKey` in `eras/conway/impl/src/Cardano/Ledger/Conway/Governance/Procedures.hs` via the stated entrypoint and trigger treasury withdrawal accounting mismatch? The investigation should test whether treasury deductions, account credits, and unclaimed withdrawals are computed consistently across proposal validation, ratification, enactment, and epoch cleanup.

## Target
- File/function: eras/conway/impl/src/Cardano/Ledger/Conway/Governance/Procedures.hs / toJSONKey
- Entrypoint: Submit governance actions for treasury withdrawals with boundary amounts, repeated recipient credentials, and concurrent account registration changes.
- Attacker controls: Treasury withdrawal map, recipient account addresses, proposal policy, proposal deposit, votes, certificates, and epoch timing.
- Exploit idea: Check whether treasury deductions, account credits, and unclaimed withdrawals are computed consistently across proposal validation, ratification, enactment, and epoch cleanup.
- Invariant to test: Governance lifecycle invariant: proposals, votes, deposits, expiry, ratification, enactment, and previous-action links must not reach an impossible or unauthorized state.
- Expected Cardano/Intersect impact: Potential Critical if value conservation is broken and ADA or native assets can be created, destroyed, or permanently frozen.
- Fast validation: Run an era-specific model/differential test comparing the implementation result with the expected STS transition and final ledger accounting.
