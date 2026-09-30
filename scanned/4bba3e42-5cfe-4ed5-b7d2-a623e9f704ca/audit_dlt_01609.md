# [?] [dos protection] increase the default spam threshold (#23301)

## Summary
Severity: Unknown
Chain: Sui
Component: MystenLabs/sui
Published: 2025-08-26
Source: https://github.com/MystenLabs/sui/commit/f5d1b6c935a2320965323b731e8f9ce35d12bf24
Type: security-commit

## Details
[dos protection] increase the default spam threshold (#23301)

## Description 

<img width="440" height="309" alt="image"
src="https://github.com/user-attachments/assets/f448f56b-657c-4b3c-9dcd-41ddafc638ef"
/>


---

## Release notes

Check each box that your changes affect. If none of the boxes relate to
your changes, release notes aren't required.

For each box you select, include information after the relevant heading
that describes the impact of your changes that a user might notice and
any actions they must take to implement updates.

- [ ] Protocol: 
- [ ] Nodes (Validators and Full nodes): 
- [ ] gRPC:
- [ ] JSON-RPC: 
- [ ] GraphQL: 
- [ ] CLI: 
- [ ] Rust SDK:

## Patch
### crates/sui-types/src/traffic_control.rs
```diff
@@ -299,7 +299,7 @@ impl PolicyConfig {
         PolicyConfig {
             client_id_source: ClientIdSource::SocketAddr,
             spam_policy_type: PolicyType::FreqThreshold(FreqThresholdConfig {
-                client_threshold: 500,
+                client_threshold: 1000,
                 window_size_secs: 5,
                 update_interval_secs: 1,
                 ..FreqThresholdConfig::default()
```
