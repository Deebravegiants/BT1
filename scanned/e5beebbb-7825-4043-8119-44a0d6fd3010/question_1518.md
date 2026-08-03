# Q1518: accept_username can mishandle duplicate actors or ordering

## Question
Can an unprivileged attacker pass duplicate signers, delegates, friends, subs, or approvals into `accept_username` and make a threshold or uniqueness assumption fail open?

## Target
- File/function: substrate/frame/identity/src/lib.rs::accept_username
- Entrypoint: signed extrinsic `accept_username`
- Attacker controls: call repetition, batching order, and surrounding state
- Exploit idea: Exploit sortedness, deduplication, and self-reference edge cases in user-controlled actor sets.
- Invariant to test: Each logical actor must count exactly once, and ordering must not change authorization semantics.
- Expected Immunefi impact: Unauthorized account or call control leading to fund theft or governance capture
- Fast validation: Fuzz duplicated, aliased, and reverse-ordered actor sets and assert threshold and ownership rules stay intact.
