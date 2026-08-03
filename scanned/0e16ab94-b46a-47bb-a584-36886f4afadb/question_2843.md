# Q2843: submit_delivery_receipt can mis-handle self-reference or aliasing

## Question
Can an unprivileged attacker set user-controlled fields so source and destination, owner and beneficiary, signer and target, or two object identifiers alias the same semantic subject and drive a path the code did not intend?

## Target
- File/function: bridges/snowbridge/pallets/outbound-queue-v2/src/lib.rs::submit_delivery_receipt
- Entrypoint: public proof / message submission extrinsic `submit_delivery_receipt`
- Attacker controls: proof or signed payload contents
- Exploit idea: Test self-targeting, same-account aliasing, reused IDs, and equivalent locations or hashes that collapse distinct roles together.
- Invariant to test: Aliasing different semantic roles to the same underlying subject must not bypass checks or duplicate effects.
- Expected Immunefi impact: Forged cross-chain message or duplicated bridge payout / asset movement
- Fast validation: Try every same-subject permutation that the type system allows and compare it to the distinct-subject path.
