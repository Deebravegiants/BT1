# Q1535: poke_deposit can mishandle duplicate actors or ordering

## Question
Can an unprivileged attacker pass duplicate signers, delegates, friends, subs, or approvals into `poke_deposit` and make a threshold or uniqueness assumption fail open?

## Target
- File/function: substrate/frame/multisig/src/lib.rs::poke_deposit
- Entrypoint: public dispatch wrapper `poke_deposit`
- Attacker controls: duplicate or adversarial list ordering, batched or wrapped execution context
- Exploit idea: Exploit sortedness, deduplication, and self-reference edge cases in user-controlled actor sets.
- Invariant to test: Each logical actor must count exactly once, and ordering must not change authorization semantics.
- Expected Immunefi impact: Unauthorized account or call control leading to fund theft or governance capture
- Fast validation: Fuzz duplicated, aliased, and reverse-ordered actor sets and assert threshold and ownership rules stay intact.
