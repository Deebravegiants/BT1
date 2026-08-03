# Q0872: call_old_weight can desync code ownership or refcounts

## Question
Can an unprivileged attacker call `call_old_weight` and make code ownership, refcounting, or removal eligibility differ across `ContractInfoOf`, `CodeInfoOf`, and `PristineCode`?

## Target
- File/function: substrate/frame/contracts/src/lib.rs::call_old_weight
- Entrypoint: public VM / contract execution extrinsic `call_old_weight`
- Attacker controls: nested call payloads, amounts, fees, or prices, beneficiary, delegate, or target accounts
- Exploit idea: Search for paths where code references are created, reused, or removed across partial failure or repeated execution.
- Invariant to test: A code hash must have exactly the owners and live references recorded by storage.
- Expected Immunefi impact: Unauthorized code/call execution or theft from contract-controlled funds
- Fast validation: Upload, instantiate, remove, and reuse the same code hash across multiple accounts and assert refcount accuracy under all failures.
