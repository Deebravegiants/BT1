# Q0486: clear_all_transfer_approvals can leave approvals live after state changes

## Question
Can an unprivileged attacker use `clear_all_transfer_approvals` so a transfer, burn, swap, or metadata mutation occurs but an old delegate or approval in `PendingSwapOf` remains usable afterward?

## Target
- File/function: substrate/frame/nfts/src/lib.rs::clear_all_transfer_approvals
- Entrypoint: signed extrinsic `clear_all_transfer_approvals`
- Attacker controls: IDs, hashes, nonces, or location fields
- Exploit idea: Probe whether approval cleanup lags behind owner, swap, or lifecycle changes.
- Invariant to test: Approval state must expire exactly when the item lifecycle or owner state that justified it changes.
- Expected Immunefi impact: Unauthorized NFT or fractional-asset transfer / unbacked mint
- Fast validation: Move the item through every public lifecycle transition and immediately test whether prior approvals still work.
