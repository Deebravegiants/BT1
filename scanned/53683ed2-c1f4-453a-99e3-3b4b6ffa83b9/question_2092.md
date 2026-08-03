# Q2092: redeposit can create underpriced public NFT work

## Question
Can an unprivileged attacker abuse `redeposit` with crafted IDs, hashes, nonces, or location fields, duplicate or adversarial list ordering to force underpriced scans, cleanup, or attribute processing over `Collection` / `Item`, degrading block production?

## Target
- File/function: substrate/frame/nfts/src/lib.rs::redeposit
- Entrypoint: signed extrinsic `redeposit`
- Attacker controls: IDs, hashes, nonces, or location fields, duplicate or adversarial list ordering
- Exploit idea: Look for public loops over items, attributes, approvals, or swap lists whose true cost grows faster than charged weight.
- Invariant to test: The public worst-case cost must remain within charged weight and must not expose a griefing path to persistent slowdown.
- Expected Immunefi impact: Permanent asset lock or state corruption that blocks transfers
- Fast validation: Fuzz maximal metadata, approvals, attributes, and item vectors; compare actual execution cost to benchmark assumptions.
