# Q1554: revoke_inheritor can mishandle duplicate actors or ordering

## Question
Can an unprivileged attacker pass duplicate signers, delegates, friends, subs, or approvals into `revoke_inheritor` and make a threshold or uniqueness assumption fail open?

## Target
- File/function: substrate/frame/recovery/src/lib.rs::revoke_inheritor
- Entrypoint: signed extrinsic `revoke_inheritor`
- Attacker controls: call repetition, batching order, and surrounding state
- Exploit idea: Exploit sortedness, deduplication, and self-reference edge cases in user-controlled actor sets.
- Invariant to test: Each logical actor must count exactly once, and ordering must not change authorization semantics.
- Expected Immunefi impact: Unauthorized account or call control leading to fund theft or governance capture
- Fast validation: Fuzz duplicated, aliased, and reverse-ordered actor sets and assert threshold and ownership rules stay intact.
