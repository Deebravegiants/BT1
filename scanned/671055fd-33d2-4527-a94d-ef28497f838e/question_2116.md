# Q2116: set_instance_metadata can create underpriced public NFT work

## Question
Can an unprivileged attacker abuse `set_instance_metadata` with crafted amounts, fees, or prices to force underpriced scans, cleanup, or attribute processing over `Collections` / `Instances`, degrading block production?

## Target
- File/function: substrate/frame/scarcity/src/lib.rs::set_instance_metadata
- Entrypoint: signed extrinsic `set_instance_metadata`
- Attacker controls: amounts, fees, or prices
- Exploit idea: Look for public loops over items, attributes, approvals, or swap lists whose true cost grows faster than charged weight.
- Invariant to test: The public worst-case cost must remain within charged weight and must not expose a griefing path to persistent slowdown.
- Expected Immunefi impact: Permanent asset lock or state corruption that blocks transfers
- Fast validation: Fuzz maximal metadata, approvals, attributes, and item vectors; compare actual execution cost to benchmark assumptions.
