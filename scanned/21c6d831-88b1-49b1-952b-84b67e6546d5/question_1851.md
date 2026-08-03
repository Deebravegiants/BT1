# Q1851: set_team can bypass collection or item locks

## Question
Can an unprivileged attacker combine `set_team` with ordinary public flows to mutate, transfer, burn, or unlock an NFT that should remain blocked by item or collection lock state?

## Target
- File/function: substrate/frame/nfts/src/lib.rs::set_team
- Entrypoint: signed extrinsic `set_team`
- Attacker controls: IDs, hashes, nonces, or location fields
- Exploit idea: Look for paths that consult one lock layer but ignore another, or consume approval state before the final lock check.
- Invariant to test: Any item blocked by lock, freeze, or wrapper constraints must remain unreachable through all public flows.
- Expected Immunefi impact: Unauthorized NFT or fractional-asset transfer / unbacked mint
- Fast validation: Activate every relevant lock variant and assert the call cannot bypass it directly or through batching or proxying.
