# [?] graph, firehose: fix panick because of re-use of an already completed stream (#2843)

## Summary
Severity: Unknown
Chain: The Graph
Component: graphprotocol/graph-node
Published: 2021-10-06
Source: https://github.com/graphprotocol/graph-node/commit/a21731f8c77f3ce94876fdad74aa6a859e89e7ef
Type: security-commit

## Details
graph, firehose: fix panick because of re-use of an already completed stream (#2843)

* graph, firehose: fix panick because of re-use of an already completed stream

The state machine of the FirehoseBlockStream was not properly resetting the state to disconnected on error leading to the usage of an already completed future leading to a panic.

All code paths are not properly returning the state to Disconnected so the stream can be re-created to contact the remote Firehose endpoint.

## Patch
### graph/src/blockchain/firehose_block_stream.rs
```diff
@@ -39,7 +39,7 @@ impl<C: Blockchain, F: FirehoseMapper<C>> Clone for FirehoseBlockStreamContext<C
 }
 
 enum BlockStreamState {
-    Disconneted,
+    Disconnected,
     Connecting(
         Pin<
             Box<
@@ -76,7 +76,7 @@ where
     ) -> Self {
         FirehoseBlockStream {
             endpoint,
-            state: BlockStreamState::Disconneted,
+            state: BlockStreamState::Disconnected,
             ctx: FirehoseBlockStreamContext {
                 cursor,
                 mapper,
@@ -99,7 +99,7 @@ impl<C: Blockchain, F: FirehoseMapper<C>> Stream for FirehoseBlockStream<C, F> {
     fn poll_next(mut self: Pin<&mut Self>, cx: &mut Context<'_>) -> Poll<Option<Self::Item>> {
         loop {
             match &mut self.state {
-                BlockStreamState::Disconneted => {
+                BlockStreamState::Disconnected => {
                     info!(
                         self.ctx.logger,
                         "Blockstream disconnected, (re-)connecting"; "endpoint uri" => format_args!("{}", self.endpoint),
@@ -144,6 +144,8 @@ impl<C: Blockchain, F: FirehoseMapper<C>> Stream for FirehoseBlockStream<C, F> {
 
                         Poll::Ready(Err(e)) => {
                             error!(self.ctx.logger, "Unable to connect to endpoint {}", e);
+                            self.state = BlockStreamState::Disconnected;
+
                             return self.schedule_error_retry(cx);
                         }
 
@@ -170,6 +172,8 @@ impl<C: Blockchain, F: FirehoseMapper<C>> Stream for FirehoseBlockStream<C, F> {
 
                         Poll::Ready(Err(e)) => {
                             error!(self.ctx.logger, "Unable to connect to endpoint {}", e);
+                            self.state = BlockStreamState::Disconnected;
+
                             return self.schedule_error_retry(cx);
                         }
 
@@ -178,7 +182,6 @@ impl<C: Blockchain, F: FirehoseMapper<C>> Stream for FirehoseBlockStream<C, F> {
                                 self.ctx.logger,
                                 "Connection is still pending when being wake up"
                             );
-
                             return Poll::Pending;
                         }
                     }
@@ -200,7 +203,7 @@ impl<C: Blockchain, F: FirehoseMapper<C>> Stream for FirehoseBlockStream<C, F> {
                                     self.ctx.logger,
                                     "Mapping block to BlockStreamEvent failed {}", e
                                 );
-                                self.state = BlockStreamState::Disconneted;
+                                self.state = BlockStreamState::Disconnected;
 
                                 return self.schedule_error_retry(cx);
                             }
@@ -209,14 +212,14 @@ impl<C: Blockchain, F: FirehoseMapper<C>> Stream for FirehoseBlockStream<C, F> {
 
                     Poll::Ready(Some(Err(e))) => {
                         error!(self.ctx.logger, "Stream disconnected from endpoint {}", e);
-                        self.state = BlockStreamState::Disconneted;
+                        self.state = BlockStreamState::Disconnected;
 
                         return self.schedule_error_retry(cx);
                     }
 
                     Poll::Ready(None) => {
                         error!(self.ctx.logger, "Stream has terminated blocks range, we expect never ending stream right now");
-                        self.state = BlockStreamState::Disconneted;
+                        self.state = BlockStreamState::Disconnected;
 
                         return self.schedule_error_retry(cx);
                     }
```
