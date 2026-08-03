# Q0520: mint can leave approvals live after state changes

## Question
Can an unprivileged attacker use `mint` so a transfer, burn, swap, or metadata mutation occurs but an old delegate or approval in `Metadata` remains usable afterward?

## Target
- File/function: substrate/frame/scarcity/src/lib.rs::mint
- Entrypoint: signed extrinsic `mint`
- Attacker controls: IDs, hashes, nonces, or location fields, beneficiary, delegate, or target accounts, duplicate or adversarial list ordering
- Exploit idea: Probe whether approval cleanup lags behind owner, swap, or lifecycle changes.
- Invariant to test: Approval state must expire exactly when the item lifecycle or owner state that justified it changes.
- Expected Immunefi impact: Unauthorized NFT or fractional-asset transfer / unbacked mint
- Fast validation: Move the item through every public lifecycle transition and immediately test whether prior approvals still work.
