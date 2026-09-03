# Q1365: hook/reentrancy timing: a preHookContract that changes token bal [when the relay path is used wi]

## Question
Can an unprivileged attacker register a preHookContract that changes token balances before the pre-snapshot in getBalancesForArray, where preTransact runs before oldBalances is read, so the state the balance equation validated differs from the state present when nullifiers and commitments are written, letting them mint unbacked leaves or double-spend, specifically when the relay path is used with a zero effective fee (where the relay branch changes the value split)?

## Target
- File/function: contracts/Hinkal.sol :: transact / _internalTransact (pre/post hooks)
- Entrypoint: Hinkal.transact
- Attacker controls: hookData.preHookContract/postHookContract, externalAddress, hook logic
- Exploit idea: mutate accounting-relevant state across the check-to-write gap
- Invariant to test: state the balance equation checked == state when insertNullifiers/insertCommitments run
- Expected Immunefi impact: Critical: minting shielded value without backing (protocol insolvency)
- Fast validation: Foundry: deploy a hook, mutate balance mid-tx, assert leaf/vault divergence
