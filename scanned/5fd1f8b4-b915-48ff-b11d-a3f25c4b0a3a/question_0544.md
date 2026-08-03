# Q0544: set_price can leave approvals live after state changes

## Question
Can an unprivileged attacker use `set_price` so a transfer, burn, swap, or metadata mutation occurs but an old delegate or approval in `Approvals` remains usable afterward?

## Target
- File/function: substrate/frame/uniques/src/lib.rs::set_price
- Entrypoint: signed extrinsic `set_price`
- Attacker controls: amounts, fees, or prices, IDs, hashes, nonces, or location fields
- Exploit idea: Probe whether approval cleanup lags behind owner, swap, or lifecycle changes.
- Invariant to test: Approval state must expire exactly when the item lifecycle or owner state that justified it changes.
- Expected Immunefi impact: Unauthorized NFT or fractional-asset transfer / unbacked mint
- Fast validation: Move the item through every public lifecycle transition and immediately test whether prior approvals still work.
