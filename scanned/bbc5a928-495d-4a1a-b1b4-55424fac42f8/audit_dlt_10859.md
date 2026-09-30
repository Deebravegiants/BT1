# [?] [chain]fix chain panic.

## Summary
Severity: Unknown
Chain: Starcoin
Component: starcoinorg/starcoin
Published: 2020-05-15
Source: https://github.com/starcoinorg/starcoin/commit/8d2ca05de2f40eeee1b5d547d3ece676adcda585
Type: security-commit

## Details
[chain]fix chain panic.

## Patch
### chain/src/chain.rs
```diff
@@ -230,7 +230,6 @@ where
     }
 
     fn get_header(&self, hash: HashValue) -> Result<Option<BlockHeader>> {
-        assert!(self.exist_block(hash));
         let header = if let Some(block) = self.get_block(hash)? {
             Some(block.header().clone())
         } else {
@@ -335,7 +334,6 @@ where
             Some(hash) => hash,
             None => self.current_header().id(),
         };
-        assert!(self.exist_block(id));
         self.storage.get_block_info(id)
     }
 
```
