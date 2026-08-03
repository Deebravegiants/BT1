# Q0600: eth_call can misaccount storage deposits

## Question
Can an unprivileged attacker use `eth_call` so storage deposit is charged, refunded, or transferred inconsistently with actual code or contract storage lifetime?

## Target
- File/function: substrate/frame/revive/src/lib.rs::eth_call
- Entrypoint: public VM / contract execution extrinsic `eth_call`
- Attacker controls: nested call payloads, amounts, fees, or prices, beneficiary, delegate, or target accounts
- Exploit idea: Probe creation, removal, overwrite, and failure paths where storage ownership and deposit ownership can diverge.
- Invariant to test: Storage deposits must track real persisted state exactly once across upload, instantiate, call, and cleanup flows.
- Expected Immunefi impact: Unauthorized code/call execution or theft from contract-controlled funds
- Fast validation: Track deposit balances and code or contract liveness through upload, instantiate, remove, and failed execution paths.
