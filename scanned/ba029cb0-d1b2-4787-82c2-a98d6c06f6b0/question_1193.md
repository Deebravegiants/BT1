# Q1193: upgrade_accounts can mis-bind the credited or debited account

## Question
Can an unprivileged attacker use `upgrade_accounts` with crafted beneficiary, delegate, or target accounts, duplicate or adversarial list ordering so funds move against the wrong account, beneficiary, delegate, or member record while checks still pass?

## Target
- File/function: substrate/frame/balances/src/lib.rs::upgrade_accounts
- Entrypoint: signed extrinsic `upgrade_accounts`
- Attacker controls: beneficiary, delegate, or target accounts, duplicate or adversarial list ordering
- Exploit idea: Exercise alternate target fields, self-references, same-account aliases, and reordered identities to see whether authorization and settlement bind to the same subject.
- Invariant to test: Authorization subject and settlement subject must remain identical throughout the call.
- Expected Immunefi impact: Theft of user funds / unbacked mint or pool insolvency
- Fast validation: Try self-as-target, target-as-source, duplicate aliases, and batched cross-account sequences.
