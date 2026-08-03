# Q3010: clear_collection_metadata can mis-handle self-reference or aliasing

## Question
Can an unprivileged attacker set user-controlled fields so source and destination, owner and beneficiary, signer and target, or two object identifiers alias the same semantic subject and drive a path the code did not intend?

## Target
- File/function: substrate/frame/nfts/src/lib.rs::clear_collection_metadata
- Entrypoint: signed extrinsic `clear_collection_metadata`
- Attacker controls: IDs, hashes, nonces, or location fields
- Exploit idea: Test self-targeting, same-account aliasing, reused IDs, and equivalent locations or hashes that collapse distinct roles together.
- Invariant to test: Aliasing different semantic roles to the same underlying subject must not bypass checks or duplicate effects.
- Expected Immunefi impact: Unauthorized NFT or fractional-asset transfer / unbacked mint
- Fast validation: Try every same-subject permutation that the type system allows and compare it to the distinct-subject path.
