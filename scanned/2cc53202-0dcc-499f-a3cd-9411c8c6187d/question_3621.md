# Q3621: Previous governance action link can be bypassed with ordering edge case in PredicateFailure

## Question
Can an unprivileged attacker exercise `PredicateFailure` in `eras/conway/impl/src/Cardano/Ledger/Conway/Rules/Enact.hs` via the stated entrypoint and trigger governance previous-action chain bypass? The investigation should test whether previous-action validation is performed before a proposal forest mutation that changes which action is considered the latest enacted or active action.

## Target
- File/function: eras/conway/impl/src/Cardano/Ledger/Conway/Rules/Enact.hs / PredicateFailure
- Entrypoint: Submit proposal procedures that reference previous governance action IDs near expiry, enactment, or sibling-removal boundaries.
- Attacker controls: GovActionId references, proposal purpose, proposal ordering, epoch, votes, deposits, and enactment timing.
- Exploit idea: Check whether previous-action validation is performed before a proposal forest mutation that changes which action is considered the latest enacted or active action.
- Invariant to test: Governance lifecycle invariant: proposals, votes, deposits, expiry, ratification, enactment, and previous-action links must not reach an impossible or unauthorized state.
- Expected Cardano/Intersect impact: Potential Critical if an unauthorized governance, treasury, protocol-parameter, committee, constitution, or hard-fork action can be enacted.
- Fast validation: Run an era-specific model/differential test comparing the implementation result with the expected STS transition and final ledger accounting.
