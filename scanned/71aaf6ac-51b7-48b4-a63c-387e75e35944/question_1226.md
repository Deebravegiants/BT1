# Q1226: create_with_pool_id can mis-bind the credited or debited account

## Question
Can an unprivileged attacker use `create_with_pool_id` with crafted amounts, fees, or prices, IDs, hashes, nonces, or location fields so funds move against the wrong account, beneficiary, delegate, or member record while checks still pass?

## Target
- File/function: substrate/frame/nomination-pools/src/lib.rs::create_with_pool_id
- Entrypoint: signed extrinsic `create_with_pool_id`
- Attacker controls: amounts, fees, or prices, IDs, hashes, nonces, or location fields
- Exploit idea: Exercise alternate target fields, self-references, same-account aliases, and reordered identities to see whether authorization and settlement bind to the same subject.
- Invariant to test: Authorization subject and settlement subject must remain identical throughout the call.
- Expected Immunefi impact: Theft of user funds / unbacked mint or pool insolvency
- Fast validation: Try self-as-target, target-as-source, duplicate aliases, and batched cross-account sequences.
