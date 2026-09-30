# [?] starknet_os: fix get_block_hash early-block underflow in buffer hint (#14452)

## Summary
Severity: Unknown
Chain: Starknet
Component: starkware-libs/sequencer
Published: 2026-06-11
Source: https://github.com/starkware-libs/sequencer/commit/9397dd9ab234d9102a1051201e1e69179112cdb3
Type: security-commit

## Details
starknet_os: fix get_block_hash early-block underflow in buffer hint (#14452)

For current_block_number < STORED_BLOCK_HASH_BUFFER the felt subtraction
current - buffer underflowed, so the hint reported "not in buffer" and the Cairo
program then hit assert_nn_le(request, current - buffer), which also underflowed
and aborted the OS while blockifier reverted the syscall gracefully. This
committed-but-unprovable block caused a reorg on the first 10 blocks of a fresh
chain. Guard the subtraction so early blocks are treated as in-buffer, matching
blockifier's block_number_in_range.

https://claude.ai/code/session_01VojMWzQzxTF7APVG7hzqnZ

## Patch
### crates/starknet_os/src/hints/hint_implementation/execute_syscalls.rs
```diff
@@ -10,8 +10,8 @@ pub(crate) fn is_block_number_in_block_hash_buffer(mut ctx: HintContext<'_>) ->
     let request_block_number = ctx.get_integer(Ids::RequestBlockNumber)?;
     let current_block_number = ctx.get_integer(Ids::CurrentBlockNumber)?;
     let stored_block_hash_buffer = ctx.fetch_const(Const::StoredBlockHashBuffer)?;
-    let is_block_number_in_block_hash_buffer =
-        request_block_number > current_block_number - stored_block_hash_buffer;
+    let is_block_number_in_block_hash_buffer = current_block_number < *stored_block_hash_buffer
+        || request_block_number > current_block_number - stored_block_hash_buffer;
     ctx.insert_value(
         Ids::IsBlockNumberInBlockHashBuffer,
         Felt::from(is_block_number_in_block_hash_buffer),
```
