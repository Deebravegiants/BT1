# [?] [chain]fix panic.

## Summary
Severity: Unknown
Chain: Starcoin
Component: starcoinorg/starcoin
Published: 2020-04-30
Source: https://github.com/starcoinorg/starcoin/commit/23a80bb8eca9b26a60e9b911f6b253100934e9c7
Type: security-commit

## Details
[chain]fix panic.

## Patch
### chain/src/lib.rs
```diff
@@ -101,11 +101,11 @@ where
 
     fn handle(&mut self, msg: ChainRequest, _ctx: &mut Self::Context) -> Self::Result {
         match msg {
-            ChainRequest::CurrentHeader() => Ok(ChainResponse::BlockHeader(Box::new(
+            ChainRequest::CurrentHeader() => Ok(ChainResponse::BlockHeader(Box::new(Some(
                 self.service.master_head_header(),
-            ))),
+            )))),
             ChainRequest::GetHeaderByHash(hash) => Ok(ChainResponse::BlockHeader(Box::new(
-                self.service.get_header_by_hash(hash)?.unwrap(),
+                self.service.get_header_by_hash(hash)?,
             ))),
             ChainRequest::HeadBlock() => Ok(ChainResponse::Block(Box::new(
                 self.service.master_head_block(),
@@ -239,10 +239,11 @@ where
             .unwrap()
             .unwrap()
         {
-            Some(*header)
-        } else {
-            None
+            if let Some(h) = *header {
+                return Some(h);
+            }
         }
+        None
     }
 
     async fn get_block_by_hash(self, hash: HashValue) -> Result<Block> {
@@ -309,10 +310,11 @@ where
             .unwrap()
             .unwrap()
         {
-            Some(*header)
-        } else {
-            None
+            if let Some(h) = *header {
+                return Some(h);
+            }
         }
+        None
     }
 
     async fn master_head_block(self) -> Option<Block> {
```

### chain/src/message/mod.rs
```diff
@@ -43,7 +43,7 @@ pub enum ChainResponse {
     Block(Box<Block>),
     OptionBlock(Option<Box<Block>>),
     OptionBlockInfo(Option<BlockInfo>),
-    BlockHeader(Box<BlockHeader>),
+    BlockHeader(Box<Option<BlockHeader>>),
     HashValue(HashValue),
     StartupInfo(StartupInfo),
     ChainInfo(ChainInfo),
```
