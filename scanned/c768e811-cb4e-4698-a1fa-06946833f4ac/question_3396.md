# Q3396: payout_stakers_by_page can leave stale references after ownership or role changes

## Question
Can an unprivileged attacker use `payout_stakers_by_page` near an ownership, beneficiary, or role change and leave stale references that still authorize or settle as if the old subject were active?

## Target
- File/function: substrate/frame/staking/src/pallet/mod.rs::payout_stakers_by_page
- Entrypoint: signed extrinsic `payout_stakers_by_page`
- Attacker controls: call repetition, batching order, and surrounding state
- Exploit idea: Probe transitions where one subject is replaced by another but auxiliary references are not rebuilt together.
- Invariant to test: No stale reference created before an ownership or role change may remain effective afterward.
- Expected Immunefi impact: Theft of user funds / unbacked mint or pool insolvency
- Fast validation: Change the controlling subject through one public call and immediately probe whether sibling entrypoints still honor the old subject.
