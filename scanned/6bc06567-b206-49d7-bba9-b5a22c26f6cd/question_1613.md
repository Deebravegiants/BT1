# Q1613: propose_bounty can desync voting locks from effective voting power

## Question
Can an unprivileged attacker use `propose_bounty` so voting power or delegation changes without the matching lock update, letting the same balance influence governance and move elsewhere?

## Target
- File/function: substrate/frame/bounties/src/lib.rs::propose_bounty
- Entrypoint: signed extrinsic `propose_bounty`
- Attacker controls: amounts, fees, or prices, duplicate or adversarial list ordering
- Exploit idea: Probe interactions between vote, delegate, remove, and unlock paths and the lock ledger.
- Invariant to test: Governance voting power and the lock that secures it must rise and fall together.
- Expected Immunefi impact: Unauthorized treasury, bounty, or governance outcome with financial impact
- Fast validation: Vote or delegate, then remove, unlock, proxy, or batch adjacent calls and assert no spendable governance power survives unlocked funds.
