# Q1548: remove_proxy can mishandle duplicate actors or ordering

## Question
Can an unprivileged attacker pass duplicate signers, delegates, friends, subs, or approvals into `remove_proxy` and make a threshold or uniqueness assumption fail open?

## Target
- File/function: substrate/frame/proxy/src/lib.rs::remove_proxy
- Entrypoint: public dispatch wrapper `remove_proxy`
- Attacker controls: nested call payloads, beneficiary, delegate, or target accounts, batched or wrapped execution context
- Exploit idea: Exploit sortedness, deduplication, and self-reference edge cases in user-controlled actor sets.
- Invariant to test: Each logical actor must count exactly once, and ordering must not change authorization semantics.
- Expected Immunefi impact: Unauthorized account or call control leading to fund theft or governance capture
- Fast validation: Fuzz duplicated, aliased, and reverse-ordered actor sets and assert threshold and ownership rules stay intact.
