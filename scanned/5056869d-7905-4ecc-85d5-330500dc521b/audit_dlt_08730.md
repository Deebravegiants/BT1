# [?] fix(p2p): Discv5 startup panic (op-rs/kona#1768)

## Summary
Severity: Unknown
Chain: Optimism
Component: ethereum-optimism/optimism
Published: 2025-05-14
Source: https://github.com/ethereum-optimism/optimism/commit/27db51b4834489794f038dc7ecfe94d9ea98035d
Type: security-commit

## Details
fix(p2p): Discv5 startup panic (op-rs/kona#1768)

## Patch
### crates/node/p2p/src/discv5/driver.rs
```diff
@@ -119,7 +119,6 @@ impl Discv5Driver {
         }
             .retry(ExponentialBuilder::default())
             .context(self)
-            .sleep(sleep)
             .notify(|err: &discv5::Error, dur: Duration| {
                 warn!(target: "discovery", ?err, "Failed to start discovery service [Duration: {:?}]", dur);
             })
```
