# [?] Merge bitcoin/bitcoin#33880: test: Fix race condition in IPC interface block progation test

## Summary
Severity: Unknown
Chain: Bitcoin
Component: bitcoin/bitcoin
Published: 2025-11-20
Source: https://github.com/bitcoin/bitcoin/commit/29c37651c74b61232b4c2ef6201bd26196b555af
Type: security-commit

## Details
Merge bitcoin/bitcoin#33880: test: Fix race condition in IPC interface block progation test

2578e6fc0f4af35f389cd8ff59825c874e0b72ac test: Fix race condition in IPC interface block propagation test (Fabian Jahr)

Pull request description:

  CI failed on this condition here: https://github.com/bitcoin/bitcoin/actions/runs/19395398994/job/55494696022?pr=33878#step:9:3983

  The check was added not too long ago in https://github.com/bitcoin/bitcoin/pull/33745 and the fix here switches the check to the node which actually produces the block. There are also some comments added to make the checks easier so understand.

  Closes #33884

ACKs for top commit:
  Sjors:
    re-utACK 2578e6fc0f4af35f389cd8ff59825c874e0b72ac
  maflcko:
    lgtm ACK 2578e6fc0f4af35f389cd8ff59825c874e0b72ac

Tree-SHA512: bfb7ae44aede50a00d4096e1a9922f9b8df31ce4242e12863e329d0d1e714d8cb46c852f694c32314e4bd26b524535e3a6967b7c57861a9b00cf09831a950b99

## Patch
### test/functional/interface_ipc.py
```diff
@@ -256,9 +256,11 @@ async def interrupt_wait():
             assert_equal(res.result, True)
 
             self.log.debug("Block should propagate")
-            assert_equal(self.nodes[1].getchaintips()[0]["height"], current_block_height + 1)
+            # Check that the IPC node actually updates its own chain
+            assert_equal(self.nodes[0].getchaintips()[0]["height"], current_block_height + 1)
             # Stalls if a regression causes submitBlock() to accept an invalid block:
             self.sync_all()
+            # Check that the other node accepts the block
             assert_equal(self.nodes[0].getchaintips()[0], self.nodes[1].getchaintips()[0])
 
             miniwallet.rescan_utxos()
```
