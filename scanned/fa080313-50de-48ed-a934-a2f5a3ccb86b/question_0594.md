# Q0594: instantiate_with_code_old_weight can misaccount storage deposits

## Question
Can an unprivileged attacker use `instantiate_with_code_old_weight` so storage deposit is charged, refunded, or transferred inconsistently with actual code or contract storage lifetime?

## Target
- File/function: substrate/frame/contracts/src/lib.rs::instantiate_with_code_old_weight
- Entrypoint: public VM / contract execution extrinsic `instantiate_with_code_old_weight`
- Attacker controls: amounts, fees, or prices, duplicate or adversarial list ordering
- Exploit idea: Probe creation, removal, overwrite, and failure paths where storage ownership and deposit ownership can diverge.
- Invariant to test: Storage deposits must track real persisted state exactly once across upload, instantiate, call, and cleanup flows.
- Expected Immunefi impact: Unauthorized code/call execution or theft from contract-controlled funds
- Fast validation: Track deposit balances and code or contract liveness through upload, instantiate, remove, and failed execution paths.
