# Q1914: hook/reentrancy timing: an internalTransact ETH send to a chosen [at the maximum allowed array l]

## Question
Can an unprivileged attacker register an internalTransact ETH send to a chosen externalAddress that re-enters via receive(), where transferETH hands control to the recipient mid-loop, so the state the balance equation validated differs from the state present when nullifiers and commitments are written, letting them mint unbacked leaves or double-spend, specifically at the maximum allowed array lengths (where boundary sizing exposes off-by-one behaviour)?

## Target
- File/function: contracts/Hinkal.sol :: transact / _internalTransact (pre/post hooks)
- Entrypoint: Hinkal.transact
- Attacker controls: hookData.preHookContract/postHookContract, externalAddress, hook logic
- Exploit idea: mutate accounting-relevant state across the check-to-write gap
- Invariant to test: state the balance equation checked == state when insertNullifiers/insertCommitments run
- Expected Immunefi impact: Critical: minting shielded value without backing (protocol insolvency)
- Fast validation: Foundry: deploy a hook, mutate balance mid-tx, assert leaf/vault divergence
