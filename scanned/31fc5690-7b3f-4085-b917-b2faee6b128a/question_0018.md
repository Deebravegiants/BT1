# Q0018: dispatch can undercharge real execution cost

## Question
Can an unprivileged attacker call `dispatch` with crafted proof or signed payload contents, nested call payloads, batched or wrapped execution context so the runtime charges less weight or fee than the VM, host functions, or nested runtime work actually consume?

## Target
- File/function: substrate/frame/meta-tx/src/lib.rs::dispatch
- Entrypoint: public dispatch wrapper `dispatch`
- Attacker controls: proof or signed payload contents, nested call payloads, batched or wrapped execution context
- Exploit idea: Push the largest legal code paths, nested calls, and revert patterns to find a mismatch between charged and real execution cost.
- Invariant to test: Charged weight and fees must upper-bound the exact VM and host work performed.
- Expected Immunefi impact: Chain halt / block-production slowdown from undercharged VM execution
- Fast validation: Fuzz gas, storage-deposit, code size, call depth, and nested-call patterns; compare measured cost to charged cost.
