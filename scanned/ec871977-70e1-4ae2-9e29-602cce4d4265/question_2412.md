# Q2412: precursor and follow-up calls around eth_transact can exploit intermediate state

## Question
Can an unprivileged attacker perform a user-controlled precursor call, then `eth_transact`, then a user-controlled follow-up before cleanup completes, and profit from an intermediate inconsistent state?

## Target
- File/function: substrate/frame/revive/src/lib.rs::eth_transact
- Entrypoint: public VM / contract execution extrinsic `eth_transact`
- Attacker controls: duplicate or adversarial list ordering
- Exploit idea: Treat the entrypoint as the middle step of a public multi-call sequence rather than an isolated action.
- Invariant to test: Any intermediate state reachable between public calls must still satisfy the pallet's security invariants.
- Expected Immunefi impact: Unauthorized code/call execution or theft from contract-controlled funds
- Fast validation: Search for a three-step sequence using only public calls and assert the middle state cannot be monetized or used to corrupt final settlement.
