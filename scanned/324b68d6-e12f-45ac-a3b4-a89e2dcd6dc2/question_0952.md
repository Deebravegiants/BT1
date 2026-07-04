# Q952: Governance proposal deposit can desynchronize from proposal state in decCBOR

## Question
Can an unprivileged attacker exercise `decCBOR` in `eras/conway/impl/src/Cardano/Ledger/Conway/Governance.hs` via the stated entrypoint and trigger governance proposal deposit missing or double counted? The investigation should test whether proposal deposits are charged, tracked, expired, enacted, or refunded using a state different from the proposal forest that survives the transaction or epoch transition.

## Target
- File/function: eras/conway/impl/src/Cardano/Ledger/Conway/Governance.hs / decCBOR
- Entrypoint: Submit a Conway/Dijkstra transaction containing proposal procedures, certificates, withdrawals, and return accounts that touch the same credentials.
- Attacker controls: Proposal procedures, proposal deposits, return addresses, governance action IDs, certificates, withdrawals, votes, and fee.
- Exploit idea: Check whether proposal deposits are charged, tracked, expired, enacted, or refunded using a state different from the proposal forest that survives the transaction or epoch transition.
- Invariant to test: Governance lifecycle invariant: proposals, votes, deposits, expiry, ratification, enactment, and previous-action links must not reach an impossible or unauthorized state.
- Expected Cardano/Intersect impact: Potential Critical if an unauthorized governance, treasury, protocol-parameter, committee, constitution, or hard-fork action can be enacted.
- Fast validation: Build a minimal sequence of transactions or certificates around the boundary condition and assert deposits, refunds, withdrawals, and UTxO state after each step.
