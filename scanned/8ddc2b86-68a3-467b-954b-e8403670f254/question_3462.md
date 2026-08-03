# Q3462: pay_tips can leave stale references after ownership or role changes

## Question
Can an unprivileged attacker use `pay_tips` near an ownership, beneficiary, or role change and leave stale references that still authorize or settle as if the old subject were active?

## Target
- File/function: substrate/frame/nfts/src/lib.rs::pay_tips
- Entrypoint: signed extrinsic `pay_tips`
- Attacker controls: duplicate or adversarial list ordering
- Exploit idea: Probe transitions where one subject is replaced by another but auxiliary references are not rebuilt together.
- Invariant to test: No stale reference created before an ownership or role change may remain effective afterward.
- Expected Immunefi impact: Unauthorized NFT or fractional-asset transfer / unbacked mint
- Fast validation: Change the controlling subject through one public call and immediately probe whether sibling entrypoints still honor the old subject.
