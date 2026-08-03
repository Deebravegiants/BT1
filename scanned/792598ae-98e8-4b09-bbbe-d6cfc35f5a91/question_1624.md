# Q1624: buy_ticket can desync voting locks from effective voting power

## Question
Can an unprivileged attacker use `buy_ticket` so voting power or delegation changes without the matching lock update, letting the same balance influence governance and move elsewhere?

## Target
- File/function: substrate/frame/lottery/src/lib.rs::buy_ticket
- Entrypoint: signed extrinsic `buy_ticket`
- Attacker controls: nested call payloads
- Exploit idea: Probe interactions between vote, delegate, remove, and unlock paths and the lock ledger.
- Invariant to test: Governance voting power and the lock that secures it must rise and fall together.
- Expected Immunefi impact: Unauthorized treasury, bounty, or governance outcome with financial impact
- Fast validation: Vote or delegate, then remove, unlock, proxy, or batch adjacent calls and assert no spendable governance power survives unlocked funds.
