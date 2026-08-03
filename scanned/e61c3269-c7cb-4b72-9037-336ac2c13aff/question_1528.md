# Q1528: set_primary_username can mishandle duplicate actors or ordering

## Question
Can an unprivileged attacker pass duplicate signers, delegates, friends, subs, or approvals into `set_primary_username` and make a threshold or uniqueness assumption fail open?

## Target
- File/function: substrate/frame/identity/src/lib.rs::set_primary_username
- Entrypoint: signed extrinsic `set_primary_username`
- Attacker controls: call repetition, batching order, and surrounding state
- Exploit idea: Exploit sortedness, deduplication, and self-reference edge cases in user-controlled actor sets.
- Invariant to test: Each logical actor must count exactly once, and ordering must not change authorization semantics.
- Expected Immunefi impact: Unauthorized account or call control leading to fund theft or governance capture
- Fast validation: Fuzz duplicated, aliased, and reverse-ordered actor sets and assert threshold and ownership rules stay intact.
