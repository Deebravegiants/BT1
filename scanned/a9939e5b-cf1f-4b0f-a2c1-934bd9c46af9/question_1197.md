# Q1197: register can mis-bind the credited or debited account

## Question
Can an unprivileged attacker use `register` with crafted call repetition, batching order, and surrounding state so funds move against the wrong account, beneficiary, delegate, or member record while checks still pass?

## Target
- File/function: bridges/modules/relayers/src/lib.rs::register
- Entrypoint: signed extrinsic `register`
- Attacker controls: call repetition, batching order, and surrounding state
- Exploit idea: Exercise alternate target fields, self-references, same-account aliases, and reordered identities to see whether authorization and settlement bind to the same subject.
- Invariant to test: Authorization subject and settlement subject must remain identical throughout the call.
- Expected Immunefi impact: Theft of user funds / unbacked mint or pool insolvency
- Fast validation: Try self-as-target, target-as-source, duplicate aliases, and batched cross-account sequences.
