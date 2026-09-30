# [?] Fix a race condition in abc-finalize-block

## Summary
Severity: Unknown
Chain: Bitcoin Cash
Component: bitcoin-cash-node/bitcoin-cash-node
Published: 2020-02-18
Source: https://github.com/bitcoin-cash-node/bitcoin-cash-node/commit/43b45cb22948e611cfd2a379a97b900fd71c098f
Type: security-commit

## Details
Fix a race condition in abc-finalize-block

Summary:
abc-finalize-block has a race condition where `node` may not be synced when its finalized block is checked: https://build.bitcoinabc.org/viewLog.html?buildId=29570&buildTypeId=BitcoinABC_Master_BitcoinAbcMasterUbsan&tab=buildLog&_focus=2214

This patch waits until `node` is synced before checking.  I also took the opportunity to rearrange some of the checks in
this section of the test so that checks on each node are organized together. IMO this is easier to read.

Test Plan: `test_runner.py abc-finalize-block` a bunch of times

Reviewers: #bitcoin_abc, deadalnix

Reviewed By: #bitcoin_abc, deadalnix

Differential Revision: https://reviews.bitcoinabc.org/D5304

## Patch
### test/functional/abc-finalize-block.py
```diff
@@ -276,12 +276,14 @@ def check_block():
         set_node_times([delay_node], self.mocktime)
         new_tip = alt_node.generatetoaddress(
             1, alt_node.get_deterministic_priv_key().address)[-1]
-        wait_for_tip(delay_node, new_tip)
 
         assert_equal(alt_node.getbestblockhash(), new_tip)
-        assert_equal(node.getfinalizedblockhash(), block_to_autofinalize)
         assert_equal(alt_node.getfinalizedblockhash(), block_to_autofinalize)
 
+        wait_for_tip(node, new_tip)
+        assert_equal(node.getfinalizedblockhash(), block_to_autofinalize)
+
+        wait_for_tip(delay_node, new_tip)
         self.log.info(
             "Check that finalization delay is effective on node boot")
         # Restart the new node, so the blocks have no header received time.
```
