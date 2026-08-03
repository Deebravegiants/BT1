# Q0305: instantiate_with_code_old_weight can commit side effects before a trap or revert

## Question
Can an unprivileged attacker make `instantiate_with_code_old_weight` transfer value, mutate host-side metadata, or touch `ContractInfoOf` / `CodeInfoOf` before the contract path traps, reverts, or errors?

## Target
- File/function: substrate/frame/contracts/src/lib.rs::instantiate_with_code_old_weight
- Entrypoint: public VM / contract execution extrinsic `instantiate_with_code_old_weight`
- Attacker controls: amounts, fees, or prices, duplicate or adversarial list ordering
- Exploit idea: Target late-failing VM paths after early host-side accounting or ownership updates.
- Invariant to test: A failed contract execution must roll back every side effect except those explicitly specified as irreversible.
- Expected Immunefi impact: Unauthorized code/call execution or theft from contract-controlled funds
- Fast validation: Build a contract that fails at different depths after each host interaction and assert exact rollback semantics.
