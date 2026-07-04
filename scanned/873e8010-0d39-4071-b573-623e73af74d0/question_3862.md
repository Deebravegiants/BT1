# Q3862: Governance vote authorization can use stale DRep or committee state in getRegDepositDelegTxCert

## Question
Can an unprivileged attacker exercise `getRegDepositDelegTxCert` in `eras/conway/impl/src/Cardano/Ledger/Conway/TxCert.hs` via the stated entrypoint and trigger DRep committee vote authorization stale state? The investigation should test whether vote authorization uses pre-certificate state while proposal/vote storage or ratification uses post-certificate state, accepting an unauthorized vote or dropping an authorized one.

## Target
- File/function: eras/conway/impl/src/Cardano/Ledger/Conway/TxCert.hs / getRegDepositDelegTxCert
- Entrypoint: Submit a transaction that changes DRep or committee registration state and casts votes in the same or adjacent ledger transition.
- Attacker controls: Voting procedures, DRep credentials, committee hot/cold credentials, certificates, vote order, proposal IDs, and witnesses.
- Exploit idea: Check whether vote authorization uses pre-certificate state while proposal/vote storage or ratification uses post-certificate state, accepting an unauthorized vote or dropping an authorized one.
- Invariant to test: Governance lifecycle invariant: proposals, votes, deposits, expiry, ratification, enactment, and previous-action links must not reach an impossible or unauthorized state.
- Expected Cardano/Intersect impact: Potential Critical if an unauthorized governance, treasury, protocol-parameter, committee, constitution, or hard-fork action can be enacted.
- Fast validation: Build a minimal sequence of transactions or certificates around the boundary condition and assert deposits, refunds, withdrawals, and UTxO state after each step.
