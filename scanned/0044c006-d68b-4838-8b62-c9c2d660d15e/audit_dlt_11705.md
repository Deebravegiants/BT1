# [?] Fix crash when indexing a block with no transactions (#86)

## Summary
Severity: Unknown
Chain: Bitcoin
Component: ordinals/ord
Published: 2022-02-01
Source: https://github.com/ordinals/ord/commit/0983b63c3927a9d28ecbc5bea195903646c86b79
Type: security-commit

## Details
Fix crash when indexing a block with no transactions (#86)

## Patch
### src/index.rs
```diff
@@ -55,7 +55,7 @@ impl Index {
         coinbase_inputs.push_front((start.n(), (start + h.subsidy()).n()));
       }
 
-      for tx in &block.txdata[1..] {
+      for tx in block.txdata.iter().skip(1) {
         let mut input_ordinal_ranges = VecDeque::new();
         for input in &tx.input {
           let mut key = Vec::new();
@@ -100,8 +100,7 @@ impl Index {
         coinbase_inputs.extend(&input_ordinal_ranges);
       }
 
-      {
-        let tx = &block.txdata[0];
+      if let Some(tx) = block.txdata.first() {
         for (vout, output) in tx.output.iter().enumerate() {
           let mut ordinals = Vec::new();
           let mut remaining = output.value;
```

### tests/find.rs
```diff
@@ -77,3 +77,13 @@ fn first_satoshi_spent_in_second_block_slot() -> Result {
     .transaction(&[(0, 0, 0)], 1)
     .run()
 }
+
+#[test]
+fn regression_empty_block_crash() -> Result {
+  Test::new()?
+    .command("find --blocksdir blocks 0 --slot --as-of-height 1")
+    .block()
+    .block_without_coinbase()
+    .expected_stdout("0.0.0.0\n")
+    .run()
+}
```

### tests/integration.rs
```diff
@@ -160,6 +160,25 @@ impl Test {
     self
   }
 
+  fn block_without_coinbase(mut self) -> Self {
+    if self.blocks.is_empty() {
+      self.blocks.push(genesis_block(Network::Bitcoin));
+    } else {
+      self.blocks.push(Block {
+        header: BlockHeader {
+          version: 0,
+          prev_blockhash: self.blocks.last().unwrap().block_hash(),
+          merkle_root: Default::default(),
+          time: 0,
+          bits: 0,
+          nonce: 0,
+        },
+        txdata: Vec::new(),
+      });
+    }
+    self
+  }
+
   fn transaction(mut self, slots: &[(usize, usize, u32)], output_count: u64) -> Self {
     let value = slots
       .iter()
```
