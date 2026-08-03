# Q0022: eth_instantiate_with_code can undercharge real execution cost

## Question
Can an unprivileged attacker call `eth_instantiate_with_code` with crafted amounts, fees, or prices, duplicate or adversarial list ordering so the runtime charges less weight or fee than the VM, host functions, or nested runtime work actually consume?

## Target
- File/function: substrate/frame/revive/src/lib.rs::eth_instantiate_with_code
- Entrypoint: public VM / contract execution extrinsic `eth_instantiate_with_code`
- Attacker controls: amounts, fees, or prices, duplicate or adversarial list ordering
- Exploit idea: Push the largest legal code paths, nested calls, and revert patterns to find a mismatch between charged and real execution cost.
- Invariant to test: Charged weight and fees must upper-bound the exact VM and host work performed.
- Expected Immunefi impact: Chain halt / block-production slowdown from undercharged VM execution
- Fast validation: Fuzz gas, storage-deposit, code size, call depth, and nested-call patterns; compare measured cost to charged cost.
