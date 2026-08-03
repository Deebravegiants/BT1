# Q1180: touch_other can mis-bind the credited or debited account

## Question
Can an unprivileged attacker use `touch_other` with crafted IDs, hashes, nonces, or location fields, beneficiary, delegate, or target accounts so funds move against the wrong account, beneficiary, delegate, or member record while checks still pass?

## Target
- File/function: substrate/frame/assets/src/lib.rs::touch_other
- Entrypoint: signed extrinsic `touch_other`
- Attacker controls: IDs, hashes, nonces, or location fields, beneficiary, delegate, or target accounts
- Exploit idea: Exercise alternate target fields, self-references, same-account aliases, and reordered identities to see whether authorization and settlement bind to the same subject.
- Invariant to test: Authorization subject and settlement subject must remain identical throughout the call.
- Expected Immunefi impact: Theft of user funds / unbacked mint or pool insolvency
- Fast validation: Try self-as-target, target-as-source, duplicate aliases, and batched cross-account sequences.
