# Q0851: buy_ticket can act on stale metadata ownership

## Question
Can an unprivileged attacker use `buy_ticket` after the underlying governance object changed lifecycle stage and still mutate or clear metadata they should no longer control?

## Target
- File/function: substrate/frame/lottery/src/lib.rs::buy_ticket
- Entrypoint: signed extrinsic `buy_ticket`
- Attacker controls: nested call payloads
- Exploit idea: Test owner binding across closure, cancellation, execution, and index reuse.
- Invariant to test: Metadata authority must expire exactly when the referenced governance object does.
- Expected Immunefi impact: Unauthorized treasury, bounty, or governance outcome with financial impact
- Fast validation: Drive the object through each lifecycle transition and immediately attempt metadata mutation or clearing from every previously-valid actor.
