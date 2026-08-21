# Q0733: Failure to bind capture artifacts to the consenting identity in orb_os_version (identification.rs)

## Question
Can an unprivileged attacker make `orb_os_version` in [src/identification.rs](src/identification.rs) associate capture artifacts with the identity that is *currently* set rather than the one that was validated when the frames were captured, so a late identity change re-attributes earlier frames?

## Target
- File/function: [src/identification.rs](src/identification.rs) -> `orb_os_version` (function)
- Entrypoint: Changing the scanned identity after capture has begun
- Attacker controls: the ordering of the identity scan relative to capture
- Exploit idea: Check whether `orb_os_version` snapshots the identity at capture time or reads it at packaging time.
- Invariant to test: Artifacts are bound to the identity validated at their capture instant, immutably.
- Expected Immunefi impact: Another person's captured frames packaged under the attacker's identity
- Fast validation: Integration test changing identity mid-flow and asserting artifacts keep their capture-time binding.
