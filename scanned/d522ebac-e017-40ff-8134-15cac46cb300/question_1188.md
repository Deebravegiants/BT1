# Q1188: create_swap can mis-bind the credited or debited account

## Question
Can an unprivileged attacker use `create_swap` with crafted beneficiary, delegate, or target accounts so funds move against the wrong account, beneficiary, delegate, or member record while checks still pass?

## Target
- File/function: substrate/frame/atomic-swap/src/lib.rs::create_swap
- Entrypoint: signed extrinsic `create_swap`
- Attacker controls: beneficiary, delegate, or target accounts
- Exploit idea: Exercise alternate target fields, self-references, same-account aliases, and reordered identities to see whether authorization and settlement bind to the same subject.
- Invariant to test: Authorization subject and settlement subject must remain identical throughout the call.
- Expected Immunefi impact: Theft of user funds / unbacked mint or pool insolvency
- Fast validation: Try self-as-target, target-as-source, duplicate aliases, and batched cross-account sequences.
