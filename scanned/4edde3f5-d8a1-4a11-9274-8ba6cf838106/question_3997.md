# Q3997: set_metadata can mishandle duplicate or reordered list elements

## Question
Can an unprivileged attacker pass duplicate, reordered, or alias-heavy list elements to `set_metadata` and make a public loop over the same logical subject count twice or skip a required check?

## Target
- File/function: substrate/frame/assets/src/lib.rs::set_metadata
- Entrypoint: signed extrinsic `set_metadata`
- Attacker controls: IDs, hashes, nonces, or location fields, duplicate or adversarial list ordering
- Exploit idea: Exploit implicit uniqueness assumptions in vectors, bounded vectors, or multi-target APIs.
- Invariant to test: Each logical subject referenced by a public list input must be processed exactly once with authorization and accounting preserved.
- Expected Immunefi impact: Theft of user funds / unbacked mint or pool insolvency
- Fast validation: Fuzz duplicate, sorted, reverse-sorted, and alias-heavy lists and assert invariant preservation.
