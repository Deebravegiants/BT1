# [?] Fix panic in log output.

## Summary
Severity: Unknown
Chain: Conflux
Component: Conflux-Chain/conflux-rust
Published: 2021-06-22
Source: https://github.com/Conflux-Chain/conflux-rust/commit/8270321a8d47bc2fd3551263eb2fdcf15d710201
Type: security-commit

## Details
Fix panic in log output.

## Patch
### core/src/pos/consensus/round_manager.rs
```diff
@@ -532,7 +532,6 @@ impl RoundManager {
         self.network.broadcast(timeout_vote_msg).await;
         diem_error!(
             round = round,
-            remote_peer = self.proposer_election.get_valid_proposer(round),
             voted = use_last_vote,
             event = LogEvent::Timeout,
         );
```
