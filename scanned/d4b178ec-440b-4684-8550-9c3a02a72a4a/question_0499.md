# Q0499: redeposit can leave approvals live after state changes

## Question
Can an unprivileged attacker use `redeposit` so a transfer, burn, swap, or metadata mutation occurs but an old delegate or approval in `PendingSwapOf` remains usable afterward?

## Target
- File/function: substrate/frame/nfts/src/lib.rs::redeposit
- Entrypoint: signed extrinsic `redeposit`
- Attacker controls: IDs, hashes, nonces, or location fields, duplicate or adversarial list ordering
- Exploit idea: Probe whether approval cleanup lags behind owner, swap, or lifecycle changes.
- Invariant to test: Approval state must expire exactly when the item lifecycle or owner state that justified it changes.
- Expected Immunefi impact: Unauthorized NFT or fractional-asset transfer / unbacked mint
- Fast validation: Move the item through every public lifecycle transition and immediately test whether prior approvals still work.
