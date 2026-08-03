# Q0887: instantiate can desync code ownership or refcounts

## Question
Can an unprivileged attacker call `instantiate` and make code ownership, refcounting, or removal eligibility differ across `ContractInfoOf`, `CodeInfoOf`, and `AddressMap`?

## Target
- File/function: substrate/frame/revive/src/lib.rs::instantiate
- Entrypoint: public VM / contract execution extrinsic `instantiate`
- Attacker controls: amounts, fees, or prices, IDs, hashes, nonces, or location fields, duplicate or adversarial list ordering
- Exploit idea: Search for paths where code references are created, reused, or removed across partial failure or repeated execution.
- Invariant to test: A code hash must have exactly the owners and live references recorded by storage.
- Expected Immunefi impact: Unauthorized code/call execution or theft from contract-controlled funds
- Fast validation: Upload, instantiate, remove, and reuse the same code hash across multiple accounts and assert refcount accuracy under all failures.
