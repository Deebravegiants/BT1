# [?] fix(cketh): guard decode_balance_batch's length arithmetic against overflow (#11566)

## Summary
Severity: Unknown
Chain: Internet Computer
Component: dfinity/ic
Published: 2026-09-16
Source: https://github.com/dfinity/ic/commit/d7a9128f01560f0bc0a7dbf753d0a3d998f46a24
Type: security-commit

## Details
fix(cketh): guard decode_balance_batch's length arithmetic against overflow (#11566)

<!-- ccr-slack-attribution -->
_Requested via [Slack
thread](https://dfinity.slack.com/archives/C09R43SKZGE/p1789374425752789?thread_ts=1789374425.752789&cid=C09R43SKZGE)_

Hardens the balance-batch length arithmetic against overflow, addressing
Mathias Björkqvist's review comment on #11549 that deferred this
hardening to a follow-up PR.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

https://claude.ai/code/session_01RBnRCq75FH338n6LdkratM

Co-authored-by: Claude <noreply@anthropic.com>

## Patch
### rs/ethereum/cketh/minter/src/balance_scan/batcher/mod.rs
```diff
@@ -211,10 +211,12 @@ pub fn encode_eth_balance_batch(holders: &[DepositAddress]) -> Vec<u8> {
 /// program can return a partial result: [`BATCHER_INITCODE`] reverts the whole call if any
 /// `balanceOf` sub-call fails, and [`ETH_BATCHER_INITCODE`] has no failure path at all — the
 /// `BALANCE` opcode makes no sub-calls. A failed batch therefore surfaces as an `eth_call` error
-/// upstream, never as a `0` here. Returns `Err` if the blob length is not exactly `n` words;
-/// never panics.
+/// upstream, never as a `0` here. Returns `Err` if the blob length is not exactly `n` words, or if
+/// `n` is so large that that length does not fit in a `usize`; never panics.
 pub fn decode_balance_batch(ret: &[u8], n: usize) -> Result<Vec<Erc20Value>, BatcherDecodeError> {
-    let expected = n * WORD;
+    let expected = n
+        .checked_mul(WORD)
+        .ok_or(BatcherDecodeError::UnrepresentableLength { entries: n })?;
     if ret.len() != expected {
         return Err(BatcherDecodeError::WrongLength {
             expected,
```

### rs/ethereum/cketh/minter/src/balance_scan/batcher/tests.rs
```diff
@@ -459,6 +459,22 @@ fn decode_wrong_length_is_err() {
     );
 }
 
+#[test]
+fn decode_unrepresentable_length_is_err() {
+    assert_eq!(
+        decode_balance_batch(&[], usize::MAX),
+        Err(BatcherDecodeError::UnrepresentableLength {
+            entries: usize::MAX
+        })
+    );
+    assert_eq!(
+        decode_balance_batch(&[], usize::MAX / WORD + 1),
+        Err(BatcherDecodeError::UnrepresentableLength {
+            entries: usize::MAX / WORD + 1
+        })
+    );
+}
+
 /// A minimal EVM instruction, enough to spell out [`BATCHER_INITCODE`] in [`assemble`].
 enum Op {
     Push1(u8),
```
