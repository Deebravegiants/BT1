# [?] Remove unnecessary check for env var about chain halt

## Summary
Severity: Unknown
Chain: Penumbra
Component: penumbra-zone/penumbra
Published: 2023-02-28
Source: https://github.com/penumbra-zone/penumbra/commit/b33b5c2245fe3cfbe3eee8099f88279fb5fe3f25
Type: security-commit

## Details
Remove unnecessary check for env var about chain halt

## Patch
### component/src/governance/view.rs
```diff
@@ -754,31 +754,11 @@ pub trait StateWriteExt: StateWrite {
             ProposalPayload::Emergency { halt_chain } => {
                 // If the proposal calls to halt the chain...
                 if *halt_chain {
-                    // Get the current halt count
-                    let halt_count = self.emergency_chain_halt_count().await?;
-
-                    // Check to see if the operator has set the environment variable indicating they
-                    // wish to resume from this particular chain halt, i.e. the chain has already halted
-                    // and they are bringing it back up again
-                    if std::env::var("PD_RESUME_FROM_EMERGENCY_HALT_PROPOSAL")
-                        .ok()
-                        .and_then(|v| v.parse::<u64>().ok()) // value of var must be number
-                        .filter(|&resume_from| resume_from == halt_count) // number must be the same as the halt count
-                        .is_some()
-                    {
-                        // If so, just print an information message, and don't halt the chain
-                        tracing::info!("resuming from emergency chain halt #{halt_count}");
-                    } else {
-                        // If not, print an informational message and signal to the consensus worker
-                        // to halt the process after the state is committed
-                        self.increment_emergency_chain_halt_count().await?;
-                        tracing::info!(
-                            "emergency proposal passed calling for immediate chain halt"
-                        );
-                        self.halt_now();
-                    }
-                } else {
-                    tracing::info!("emergency proposal without chain halt passed, nothing to do");
+                    // Print an informational message and signal to the consensus worker to halt the
+                    // process after the state is committed
+                    self.increment_emergency_chain_halt_count().await?;
+                    tracing::info!("emergency proposal passed calling for immediate chain halt");
+                    self.halt_now();
                 }
             }
             ProposalPayload::ParameterChange { old, new } => {
```
