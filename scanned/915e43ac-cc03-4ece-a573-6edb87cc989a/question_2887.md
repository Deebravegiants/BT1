# Q2887: set_reserves can mis-handle self-reference or aliasing

## Question
Can an unprivileged attacker set user-controlled fields so source and destination, owner and beneficiary, signer and target, or two object identifiers alias the same semantic subject and drive a path the code did not intend?

## Target
- File/function: substrate/frame/assets/src/lib.rs::set_reserves
- Entrypoint: signed extrinsic `set_reserves`
- Attacker controls: IDs, hashes, nonces, or location fields, duplicate or adversarial list ordering
- Exploit idea: Test self-targeting, same-account aliasing, reused IDs, and equivalent locations or hashes that collapse distinct roles together.
- Invariant to test: Aliasing different semantic roles to the same underlying subject must not bypass checks or duplicate effects.
- Expected Immunefi impact: Theft of user funds / unbacked mint or pool insolvency
- Fast validation: Try every same-subject permutation that the type system allows and compare it to the distinct-subject path.
