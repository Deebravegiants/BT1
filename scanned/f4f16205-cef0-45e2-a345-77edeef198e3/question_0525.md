# Q0525: transfer can leave approvals live after state changes

## Question
Can an unprivileged attacker use `transfer` so a transfer, burn, swap, or metadata mutation occurs but an old delegate or approval in `Metadata` remains usable afterward?

## Target
- File/function: substrate/frame/scarcity/src/lib.rs::transfer
- Entrypoint: signed extrinsic `transfer`
- Attacker controls: beneficiary, delegate, or target accounts
- Exploit idea: Probe whether approval cleanup lags behind owner, swap, or lifecycle changes.
- Invariant to test: Approval state must expire exactly when the item lifecycle or owner state that justified it changes.
- Expected Immunefi impact: Unauthorized NFT or fractional-asset transfer / unbacked mint
- Fast validation: Move the item through every public lifecycle transition and immediately test whether prior approvals still work.
