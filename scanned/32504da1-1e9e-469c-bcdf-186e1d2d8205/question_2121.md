# Q2121: buy_item can create underpriced public NFT work

## Question
Can an unprivileged attacker abuse `buy_item` with crafted IDs, hashes, nonces, or location fields to force underpriced scans, cleanup, or attribute processing over `Collection` / `Asset`, degrading block production?

## Target
- File/function: substrate/frame/uniques/src/lib.rs::buy_item
- Entrypoint: signed extrinsic `buy_item`
- Attacker controls: IDs, hashes, nonces, or location fields
- Exploit idea: Look for public loops over items, attributes, approvals, or swap lists whose true cost grows faster than charged weight.
- Invariant to test: The public worst-case cost must remain within charged weight and must not expose a griefing path to persistent slowdown.
- Expected Immunefi impact: Permanent asset lock or state corruption that blocks transfers
- Fast validation: Fuzz maximal metadata, approvals, attributes, and item vectors; compare actual execution cost to benchmark assumptions.
