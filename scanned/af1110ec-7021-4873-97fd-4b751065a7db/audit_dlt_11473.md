# [?] Fix panics in packet queries  (#554)

## Summary
Severity: Unknown
Chain: Cosmos
Component: informalsystems/hermes
Published: 2021-01-27
Source: https://github.com/informalsystems/hermes/commit/00570dd858f88010ac1dac0956a596536671192d
Type: security-commit

## Details
Fix panics in packet queries  (#554)

* Fix for #521. Will fix the unwraps for QueryUnreceivedAcknowledgementCmd also

* Added the 'required' annotation to packet queries.

When a free option (such as a chain_id or port_id) in a command
is tagged with the 'required' attribute, this will safeguard against
invoking the command with `default()` values for the corresponding
option.

* Updated the changelog

* Apply suggestions from code review

Co-authored-by: Anca Zamfir <ancazamfir@users.noreply.github.com>

* FMT fix

Co-authored-by: Anca Zamfir <ancazamfir@users.noreply.github.com>

## Patch
### CHANGELOG.md
```diff
@@ -21,7 +21,7 @@
 - [relayer-cli]
   - Replace `ChannelConfig` in `Channel::new` ([#511])
   - Add `packet-send` CLI ([#470])
-  - UX improvements for relayer txs ([#536, #540])
+  - UX improvements for relayer txs ([#536, #540, #554])
 
 - [relayer]
   - Performance improvements ([#514], [#537])
@@ -59,6 +59,7 @@
 [#536]: https://github.com/informalsystems/ibc-rs/issues/536
 [#537]: https://github.com/informalsystems/ibc-rs/issues/537
 [#540]: https://github.com/informalsystems/ibc-rs/issues/540
+[#554]: https://github.com/informalsystems/ibc-rs/issues/554
 
 
 ## v0.0.6
```

### relayer-cli/src/commands/query.rs
```diff
@@ -11,19 +11,19 @@ mod packet;
 #[derive(Command, Debug, Options, Runnable)]
 pub enum QueryCmd {
     /// The `query client` subcommand
-    #[options(help = "query client")]
+    #[options(help = "query information about client(s)")]
     Client(QueryClientCmds),
 
     /// The `query connection` subcommand
-    #[options(help = "query connection")]
+    #[options(help = "query information about connection(s)")]
     Connection(QueryConnectionCmds),
 
     /// The `query channel` subcommand
-    #[options(help = "query channel")]
+    #[options(help = "query information about channel(s)")]
     Channel(QueryChannelCmds),
 
     /// The `query packet` subcommand
-    #[options(help = "query packets")]
+    #[options(help = "query information about packet(s)")]
     Packet(QueryPacketCmds),
 }
 
```

### relayer-cli/src/commands/query/packet.rs
```diff
@@ -3,6 +3,7 @@ use std::sync::Arc;
 use abscissa_core::{Command, Options, Runnable};
 use serde_json::json;
 use tokio::runtime::Runtime as TokioRuntime;
+use tracing::info;
 
 use ibc::ics04_channel::packet::{PacketMsgType, Sequence};
 use ibc::ics24_host::identifier::{ChannelId, PortId};
@@ -20,13 +21,13 @@ use crate::prelude::*;
 
 #[derive(Clone, Command, Debug, Options)]
 pub struct QueryPacketCommitmentsCmd {
-    #[options(free, help = "identifier of the chain to query")]
+    #[options(free, required, help = "identifier of the chain to query")]
     chain_id: String,
 
-    #[options(free, help = "identifier of the port to query")]
+    #[options(free, required, help = "identifier of the port to query")]
     port_id: PortId,
 
-    #[options(free, help = "identifier of the channel to query")]
+    #[options(free, required, help = "identifier of the channel to query")]
     channel_id: ChannelId,
 
     #[options(help = "height of the state to query", short = "h")]
@@ -40,7 +41,7 @@ impl QueryPacketCommitmentsCmd {
     ) -> Result<(ChainConfig, QueryPacketOptions), String> {
         let dest_chain_config = config
             .find_chain(&self.chain_id.parse().unwrap())
-            .ok_or_else(|| "missing destination chain configuration".to_string())?;
+            .ok_or_else(|| format!("missing configuration for chain ({}) ", self.chain_id))?;
 
         let opts = QueryPacketOptions {
             port_id: self.port_id.clone(),
@@ -92,16 +93,16 @@ impl Runnable for QueryPacketCommitmentsCmd {
 
 #[derive(Clone, Command, Debug, Options)]
 pub struct QueryPacketCommitmentCmd {
-    #[options(free, help = "identifier of the chain to query")]
+    #[options(free, required, help = "identifier of the chain to query")]
     chain_id: String,
 
-    #[options(free, help = "identifier of the port to query")]
+    #[options(free, required, help = "identifier of the port to query")]
     port_id: PortId,
 
-    #[options(free, help = "identifier of the channel to query")]
+    #[options(free, required, help = "identifier of the channel to query")]
     channel_id: ChannelId,
 
-    #[options(free, help = "sequence of packet to query")]
+    #[options(free, required, help = "sequence of packet to query")]
     sequence: u64,
 
     #[options(help = "height of the state to query", short = "h")]
@@ -115,7 +116,7 @@ impl QueryPacketCommitmentCmd {
     ) -> Result<(ChainConfig, QueryPacketOptions, Sequence), String> {
         let dest_chain_config = config
             .find_chain(&self.chain_id.parse().unwrap())
-            .ok_or_else(|| "missing destination chain configuration".to_string())?;
+            .ok_or_else(|| format!("missing configuration for chain ({}) ", self.chain_id))?;
 
         let opts = QueryPacketOptions {
             port_id: self.port_id.clone(),
@@ -167,20 +168,30 @@ impl Runnable for QueryPacketCommitmentCmd {
 pub struct QueryUnreceivedPacketsCmd {
     #[options(
         free,
-        help = "identifier of the chain to query the unreceived sequences"
+        required,
+        help = "identifier of the chain to query the unreceived sequences (dst chain)"
     )]
     dst_chain_id: String,
 
     #[options(
         free,
-        help = "identifier of the chain where sent sequences are queried"
+        required,
+        help = "identifier of the chain where sent sequences are queried (source chain)"
     )]
     src_chain_id: String,
 
-    #[options(free, help = "identifier of the port to query on source chain")]
+    #[options(
+        free,
+        required,
+        help = "identifier of the port to query on source chain"
+    )]
     port_id: PortId,
 
-    #[options(free, help = "identifier of the channel to query on source chain")]
+    #[options(
+        free,
+        required,
+        help = "identifier of the channel to query on source chain"
+    )]
     channel_id: ChannelId,
 }
 
@@ -191,11 +202,11 @@ impl QueryUnreceivedPacketsCmd {
     ) -> Result<(ChainConfig, ChainConfig, QueryPacketOptions), String> {
         let src_chain_config = config
             .find_chain(&self.src_chain_id.parse().unwrap())
-            .ok_or_else(|| "missing source chain configuration".to_string())?;
+            .ok_or_else(|| format!("missing configuration for chain ({}) ", self.src_chain_id))?;
 
         let dst_chain_config = config
             .find_chain(&self.dst_chain_id.parse().unwrap())
-            .ok_or_else(|| "missing destination chain configuration".to_string())?;
+            .ok_or_else(|| format!("missing configuration for chain ({}) ", self.dst_chain_id))?;
 
         let opts = QueryPacketOptions {
             port_id: self.port_id.clone(),
@@ -224,9 +235,29 @@ impl Runnable for QueryUnreceivedPacketsCmd {
         let dst_chain = CosmosSDKChain::bootstrap(dst_chain_config, rt).unwrap();
 
         // get the channel information from source chain
-        let channel = src_chain
+        let channel_res = src_chain
             .query_channel(&opts.port_id, &opts.channel_id, Height::zero())
-            .unwrap();
+            .map_err(|e| Kind::Query.context(e));
+
+        let channel = match channel_res {
+            Ok(c) => c,
+            Err(e) => {
+                return Output::error(format!(
+                    "failed to find channel ({}/{}) on chain ({}) with error: {}",
+                    opts.port_id,
+                    opts.channel_id,
+                    src_chain.config().id,
+                    e
+                ))
+                .exit();
+            }
+        };
+
+        debug!(
+            "Fetched from source chain {} the following channel {:?}",
+            src_chain.config().id,
+            channel
+        );
 
         // get the packet commitments on source chain
         let commitments_request = QueryPacketCommitmentsRequest {
@@ -235,18 +266,40 @@ impl Runnable for QueryUnreceivedPacketsCmd {
             pagination: None,
         };
 
-        // extract the sequences
-        let sequences: Vec<u64> = src_chain
+        let seq_res = src_chain
             .query_packet_commitments(commitments_request)
-            .unwrap()
-            .0
-            .into_iter()
-            .map(|v| v.sequence)
-            .collect();
+            .map_err(|e| Kind::Query.context(e));
+
+        // extract the sequences
+        let sequences: Vec<u64> = match seq_res {
+            Ok(seqs) => seqs.0.into_iter().map(|v| v.sequence).collect(),
+            Err(e) => {
+                return Output::error(format!(
+                    "failed to fetch the packet commitments from src chain ({}) with error: {}",
+                    src_chain.config().id,
+                    e
+                ))
+                .exit()
+            }
+        };
+
+        // Extract the channel identifier which the counterparty (dst chain) is using
+        let channel_id: String = match &channel.counterparty().channel_id {
+            None => {
+                return Output::error(format!(
+                    "The channel ({}/{}) has no counterparty (channel state is {:?})",
+                    opts.port_id,
+                    opts.channel_id,
+                    *channel.state()
+                ))
+                .exit()
+            }
+            Some(id) => id.to_string(),
+        };
 
         let request = QueryUnreceivedPacketsRequest {
             port_id: channel.counterparty().port_id().to_string(),
-            channel_id: channel.counterparty().channel_id().unwrap().to_string(),
+            channel_id,
             packet_commitment_sequences: sequences,
         };
 
@@ -261,13 +314,13 @@ impl Runnable for QueryUnreceivedPacketsCmd {
 
 #[derive(Clone, Command, Debug, Options)]
 pub struct QueryPacketAcknowledgementsCmd {
-    #[options(free, help = "identifier of the chain to query")]
+    #[options(free, required, help = "identifier of the chain to query")]
     chain_id: String,
 
-    #[options(free, help = "identifier of the port to query")]
+    #[options(free, required, help = "identifier of the port to query")]
     port_id: PortId,
 
-    #[options(free, help = "identifier of the channel to query")]
+    #[options(free, required, help = "identifier of the channel to query")]
     channel_id: ChannelId,
 
     #[options(help = "height of the state to query", short = "h")]
@@ -281,7 +334,12 @@ impl QueryPacketAcknowledgementsCmd {
     ) -> Result<(ChainConfig, QueryPacketOptions), String> {
         let dest_chain_config = config
             .find_chain(&self.chain_id.parse().unwrap())
-            .ok_or_else(|| "missing destination chain configuration".to_string())?;
+            .ok_or_else(|| {
+                format!(
+                    "missing configuration for the given chain ({}) ",
+                    self.chain_id
+                )
+            })?;
 
         let opts = QueryPacketOptions {
             port_id: self.port_id.clone(),
@@ -333,16 +391,16 @@ impl Runnable for QueryPacketAcknowledgementsCmd {
 
 #[derive(Clone, Command, Debug, Options)]
 pub struct QueryPacketAcknowledgmentCmd {
-    #[options(free, help = "identifier of the chain to query")]
+    #[options(free, required, help = "identifier of the chain to query")]
     chain_id: String,
 
-    #[options(free, help = "identifier of the port to query")]
+    #[options(free, required, help = "identifier of the port to query")]
     port_id: PortId,
 
-    #[options(free, help = "identifier of the channel to query")]
+    #[options(free, required, help = "identifier of the channel to query")]
     channel_id: ChannelId,
 
-    #[options(free, help = "sequence of packet to query")]
+    #[options(free, required, help = "sequence of packet to query")]
     sequence: u64,
 
     #[options(help = "height of the state to query", short = "h")]
@@ -356,7 +414,7 @@ impl QueryPacketAcknowledgmentCmd {
     ) -> Result<(ChainConfig, QueryPacketOptions, Sequence), String> {
         let dest_chain_config = config
             .find_chain(&self.chain_id.parse().unwrap())
-            .ok_or_else(|| "missing destination chain configuration".to_string())?;
+            .ok_or_else(|| format!("missing configuration for chain ({}) ", self.chain_id))?;
 
         let opts = QueryPacketOptions {
             port_id: self.port_id.clone(),
@@ -406,19 +464,32 @@ impl Runnable for QueryPacketAcknowledgmentCmd {
 /// 3. queries the destination chain for the unreceived sequences out of the list obtained in 2.
 #[derive(Clone, Command, Debug, Options)]
 pub struct QueryUnreceivedAcknowledgementCmd {
-    #[options(free, help = "identifier of the chain to query the unreceived acks")]
+    #[options(
+        free,
+        required,
+        help = "identifier of the chain to query the unreceived acks (dst chain)"
+    )]
     dst_chain_id: String,
 
     #[options(
         free,
-        help = "identifier of the chain where received sequences are queried"
+        required,
+        help = "identifier of the chain where received sequences are queried (source chain)"
     )]
     src_chain_id: String,
 
-    #[options(free, help = "identifier of the port to query on source chain")]
+    #[options(
+        free,
+        required,
+        help = "identifier of the port to query on source chain"
+    )]
     port_id: PortId,
 
-    #[options(free, help = "identifier of the channel to query on source chain")]
+    #[options(
+        free,
+        required,
+        help = "identifier of the channel to query on source chain"
+    )]
     channel_id: ChannelId,
 }
 
@@ -429,11 +500,11 @@ impl QueryUnreceivedAcknowledgementCmd {
     ) -> Result<(ChainConfig, ChainConfig, QueryPacketOptions), String> {
         let src_chain_config = config
             .find_chain(&self.src_chain_id.parse().unwrap())
-            .ok_or_else(|| "missing destination chain configuration".to_string())?;
+            .ok_or_else(|| format!("missing configuration for chain ({}) ", self.src_chain_id))?;
 
         let dst_chain_config = config
             .find_chain(&self.dst_chain_id.parse().unwrap())
-            .ok_or_else(|| "missing destination chain configuration".to_string())?;
+            .ok_or_else(|| format!("missing configuration for chain ({}) ", self.dst_chain_id))?;
 
         let opts = QueryPacketOptions {
             port_id: self.port_id.clone(),
@@ -462,9 +533,29 @@ impl Runnable for QueryUnreceivedAcknowledgementCmd {
         let dst_chain = CosmosSDKChain::bootstrap(dst_chain_config, rt).unwrap();
 
         // get the channel information from source chain
-        let channel = src_chain
+        let channel_res = src_chain
             .query_channel(&opts.port_id, &opts.channel_id, Height::zero())
-            .unwrap();
+            .map_err(|e| Kind::Query.context(e));
+
+        let channel = match channel_res {
+            Ok(c) => c,
+            Err(e) => {
+                return Output::error(format!(
+                    "failed to find the target channel ({}/{}) on src chain ({}) with error: {}",
+                    opts.port_id,
+                    opts.channel_id,
+                    src_chain.config().id,
+                    e
+                ))
+                .exit();
+            }
+        };
+
+        debug!(
+            "Fetched from src chain {} the following channel {:?}",
+            src_chain.config().id,
+            channel
+        );
 
         // get the packet commitments on source chain
         let acks_request = QueryPacketAcknowledgementsRequest {
@@ -473,18 +564,39 @@ impl Runnable for QueryUnreceivedAcknowledgementCmd {
             pagination: None,
         };
 
-        // extract the sequences
-        let sequences: Vec<u64> = src_chain
+        let seq_res = src_chain
             .query_packet_acknowledgements(acks_request)
-            .unwrap()
-            .0
-            .into_iter()
-            .map(|v| v.sequence)
-            .collect();
+            .map_err(|e| Kind::Query.context(e));
+
+        // extract the sequences
+        let sequences: Vec<u64> = match seq_res {
+            Ok(seqs) => seqs.0.into_iter().map(|v| v.sequence).collect(),
+            Err(e) => {
+                return Output::error(format!(
+                    "failed to fetch packet acknowledgements from src chain ({}) with error: {}",
+                    src_chain.config().id,
+                    e
+                ))
+                .exit()
+            }
+        };
+
+        let channel_id = match &channel.counterparty().channel_id() {
+            None => {
+                return Output::error(format!(
+                    "The channel ({}/{}) has no counterparty (channel state is {:?})",
+                    opts.port_id,
+                    opts.channel_id,
+                    *channel.state()
+                ))
+                .exit()
+            }
+            Some(id) => id.to_string(),
+        };
 
         let request = QueryUnreceivedAcksRequest {
             port_id: channel.counterparty().port_id().to_string(),
-            channel_id: channel.counterparty().channel_id().unwrap().to_string(),
+            channel_id,
             packet_ack_sequences: sequences,
         };
 
```
