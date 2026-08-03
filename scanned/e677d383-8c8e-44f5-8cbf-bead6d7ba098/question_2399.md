# Q2399: precursor and follow-up calls around call_old_weight can exploit intermediate state

## Question
Can an unprivileged attacker perform a user-controlled precursor call, then `call_old_weight`, then a user-controlled follow-up before cleanup completes, and profit from an intermediate inconsistent state?

## Target
- File/function: substrate/frame/contracts/src/lib.rs::call_old_weight
- Entrypoint: public VM / contract execution extrinsic `call_old_weight`
- Attacker controls: nested call payloads, amounts, fees, or prices, beneficiary, delegate, or target accounts
- Exploit idea: Treat the entrypoint as the middle step of a public multi-call sequence rather than an isolated action.
- Invariant to test: Any intermediate state reachable between public calls must still satisfy the pallet's security invariants.
- Expected Immunefi impact: Unauthorized code/call execution or theft from contract-controlled funds
- Fast validation: Search for a three-step sequence using only public calls and assert the middle state cannot be monetized or used to corrupt final settlement.
