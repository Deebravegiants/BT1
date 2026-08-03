# Q3350: claim_rewards_to can leave stale references after ownership or role changes

## Question
Can an unprivileged attacker use `claim_rewards_to` near an ownership, beneficiary, or role change and leave stale references that still authorize or settle as if the old subject were active?

## Target
- File/function: bridges/modules/relayers/src/lib.rs::claim_rewards_to
- Entrypoint: signed extrinsic `claim_rewards_to`
- Attacker controls: beneficiary, delegate, or target accounts
- Exploit idea: Probe transitions where one subject is replaced by another but auxiliary references are not rebuilt together.
- Invariant to test: No stale reference created before an ownership or role change may remain effective afterward.
- Expected Immunefi impact: Theft of user funds / unbacked mint or pool insolvency
- Fast validation: Change the controlling subject through one public call and immediately probe whether sibling entrypoints still honor the old subject.
