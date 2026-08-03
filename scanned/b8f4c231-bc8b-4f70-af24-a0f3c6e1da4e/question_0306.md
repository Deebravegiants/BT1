# Q0306: remove_code can commit side effects before a trap or revert

## Question
Can an unprivileged attacker make `remove_code` transfer value, mutate host-side metadata, or touch `ContractInfoOf` / `CodeInfoOf` before the contract path traps, reverts, or errors?

## Target
- File/function: substrate/frame/contracts/src/lib.rs::remove_code
- Entrypoint: public VM / contract execution extrinsic `remove_code`
- Attacker controls: IDs, hashes, nonces, or location fields
- Exploit idea: Target late-failing VM paths after early host-side accounting or ownership updates.
- Invariant to test: A failed contract execution must roll back every side effect except those explicitly specified as irreversible.
- Expected Immunefi impact: Unauthorized code/call execution or theft from contract-controlled funds
- Fast validation: Build a contract that fails at different depths after each host interaction and assert exact rollback semantics.
