# Q1042: set_friend_groups can bind approval to the wrong payload

## Question
Can an unprivileged attacker make `set_friend_groups` approve or execute a different payload than users thought they had authorized because hashing, length, or metadata binding is incomplete?

## Target
- File/function: substrate/frame/recovery/src/lib.rs::set_friend_groups
- Entrypoint: signed extrinsic `set_friend_groups`
- Attacker controls: duplicate or adversarial list ordering
- Exploit idea: Focus on call hash, encoded length, mortality, nonce, and fallback payload mismatches.
- Invariant to test: The payload users approve must be exactly the payload the runtime executes.
- Expected Immunefi impact: Unauthorized account or call control leading to fund theft or governance capture
- Fast validation: Mutate inert-looking fields, encoded lengths, and nested-call ordering while reusing the same outer approval or signature.
