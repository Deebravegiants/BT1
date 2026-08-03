# Q1166: finish_destroy can mis-bind the credited or debited account

## Question
Can an unprivileged attacker use `finish_destroy` with crafted IDs, hashes, nonces, or location fields so funds move against the wrong account, beneficiary, delegate, or member record while checks still pass?

## Target
- File/function: substrate/frame/assets/src/lib.rs::finish_destroy
- Entrypoint: signed extrinsic `finish_destroy`
- Attacker controls: IDs, hashes, nonces, or location fields
- Exploit idea: Exercise alternate target fields, self-references, same-account aliases, and reordered identities to see whether authorization and settlement bind to the same subject.
- Invariant to test: Authorization subject and settlement subject must remain identical throughout the call.
- Expected Immunefi impact: Theft of user funds / unbacked mint or pool insolvency
- Fast validation: Try self-as-target, target-as-source, duplicate aliases, and batched cross-account sequences.
