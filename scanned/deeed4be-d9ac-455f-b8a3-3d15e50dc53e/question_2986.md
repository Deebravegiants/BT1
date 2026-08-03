# Q2986: reject_announcement can mis-handle self-reference or aliasing

## Question
Can an unprivileged attacker set user-controlled fields so source and destination, owner and beneficiary, signer and target, or two object identifiers alias the same semantic subject and drive a path the code did not intend?

## Target
- File/function: substrate/frame/proxy/src/lib.rs::reject_announcement
- Entrypoint: public dispatch wrapper `reject_announcement`
- Attacker controls: beneficiary, delegate, or target accounts, batched or wrapped execution context
- Exploit idea: Test self-targeting, same-account aliasing, reused IDs, and equivalent locations or hashes that collapse distinct roles together.
- Invariant to test: Aliasing different semantic roles to the same underlying subject must not bypass checks or duplicate effects.
- Expected Immunefi impact: Unauthorized account or call control leading to fund theft or governance capture
- Fast validation: Try every same-subject permutation that the type system allows and compare it to the distinct-subject path.
