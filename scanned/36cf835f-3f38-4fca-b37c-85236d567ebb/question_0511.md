# Q0511: update_mint_settings can leave approvals live after state changes

## Question
Can an unprivileged attacker use `update_mint_settings` so a transfer, burn, swap, or metadata mutation occurs but an old delegate or approval in `PendingSwapOf` remains usable afterward?

## Target
- File/function: substrate/frame/nfts/src/lib.rs::update_mint_settings
- Entrypoint: signed extrinsic `update_mint_settings`
- Attacker controls: IDs, hashes, nonces, or location fields
- Exploit idea: Probe whether approval cleanup lags behind owner, swap, or lifecycle changes.
- Invariant to test: Approval state must expire exactly when the item lifecycle or owner state that justified it changes.
- Expected Immunefi impact: Unauthorized NFT or fractional-asset transfer / unbacked mint
- Fast validation: Move the item through every public lifecycle transition and immediately test whether prior approvals still work.
