# [?] tests: write the notification to different files to avoid race condition

## Summary
Severity: Unknown
Chain: Bitcoin Cash
Component: bitcoin-cash-node/bitcoin-cash-node
Published: 2018-09-20
Source: https://github.com/bitcoin-cash-node/bitcoin-cash-node/commit/5ac574978d2e819948e17a3e820934aadf80192d
Type: security-commit

## Details
tests: write the notification to different files to avoid race condition

Summary:
Backport of core [[https://github.com/bitcoin/bitcoin/pull/14275 | PR14275]].

This is slighly adapted to not reduce large fork coverage but allow the
test to pass on windows.

Test Plan:
  ./test/functional/test_runner.py feature_notifications
Ran on Linux, windows (depends on D5964) and OSX for sanity.

Reviewers: #bitcoin_abc, deadalnix

Reviewed By: #bitcoin_abc, deadalnix

Differential Revision: https://reviews.bitcoinabc.org/D5966

## Patch
### test/functional/feature_notifications.py
```diff
@@ -9,7 +9,7 @@
 from test_framework.test_framework import BitcoinTestFramework
 from test_framework.util import assert_equal, connect_nodes_bi, wait_until
 
-FORK_WARNING_MESSAGE = "Warning: Large-work fork detected, forking after block {}\n"
+FORK_WARNING_MESSAGE = "Warning: Large-work fork detected, forking after block {}"
 
 
 class NotificationsTest(BitcoinTestFramework):
@@ -21,64 +21,77 @@ def skip_test_if_missing_module(self):
         self.skip_if_no_wallet()
 
     def setup_network(self):
-        self.alert_filename = os.path.join(self.options.tmpdir, "alert.txt")
-        self.block_filename = os.path.join(self.options.tmpdir, "blocks.txt")
-        self.tx_filename = os.path.join(
-            self.options.tmpdir, "transactions.txt")
+        self.alertnotify_dir = os.path.join(self.options.tmpdir, "alertnotify")
+        self.blocknotify_dir = os.path.join(self.options.tmpdir, "blocknotify")
+        self.walletnotify_dir = os.path.join(
+            self.options.tmpdir, "walletnotify")
+        os.mkdir(self.alertnotify_dir)
+        os.mkdir(self.blocknotify_dir)
+        os.mkdir(self.walletnotify_dir)
 
         # -alertnotify and -blocknotify on node0, walletnotify on node1
         self.extra_args = [["-blockversion=2",
-                            "-alertnotify=echo %s >> {}".format(
-                                self.alert_filename),
-                            "-blocknotify=echo %s >> {}".format(self.block_filename)],
+                            "-alertnotify=echo > {}".format(
+                                os.path.join(self.alertnotify_dir, '%s')),
+                            "-blocknotify=echo > {}".format(os.path.join(self.blocknotify_dir, '%s'))],
                            ["-blockversion=211",
                             "-rescan",
-                            "-walletnotify=echo %s >> {}".format(self.tx_filename)]]
+                            "-walletnotify=echo > {}".format(os.path.join(self.walletnotify_dir, '%s'))]]
         super().setup_network()
 
     def run_test(self):
         self.log.info("test -blocknotify")
         block_count = 10
         blocks = self.nodes[1].generate(block_count)
 
-        # wait at most 10 seconds for expected file size before reading the
-        # content
-        wait_until(lambda: os.path.isfile(self.block_filename) and os.stat(
-            self.block_filename).st_size >= (block_count * 65), timeout=10)
+        # wait at most 10 seconds for expected number of files before reading
+        # the content
+        wait_until(
+            lambda: len(
+                os.listdir(
+                    self.blocknotify_dir)) == block_count,
+            timeout=10)
 
-        # file content should equal the generated blocks hashes
-        with open(self.block_filename, 'r', encoding="utf-8") as f:
-            assert_equal(sorted(blocks), sorted(l.strip()
-                                                for l in f.read().splitlines()))
+        # directory content should equal the generated blocks hashes
+        assert_equal(sorted(blocks), sorted(os.listdir(self.blocknotify_dir)))
 
         self.log.info("test -walletnotify")
-        # wait at most 10 seconds for expected file size before reading the
-        # content
-        wait_until(lambda: os.path.isfile(self.tx_filename) and os.stat(
-            self.tx_filename).st_size >= (block_count * 65), timeout=10)
-
-        # file content should equal the generated transaction hashes
+        # wait at most 10 seconds for expected number of files before reading
+        # the content
+        wait_until(
+            lambda: len(
+                os.listdir(
+                    self.walletnotify_dir)) == block_count,
+            timeout=10)
+
+        # directory content should equal the generated transaction hashes
         txids_rpc = list(
             map(lambda t: t['txid'], self.nodes[1].listtransactions("*", block_count)))
-        with open(self.tx_filename, 'r', encoding="ascii") as f:
-            assert_equal(sorted(txids_rpc), sorted(l.strip()
-                                                   for l in f.read().splitlines()))
-        os.remove(self.tx_filename)
+        assert_equal(
+            sorted(txids_rpc), sorted(
+                os.listdir(
+                    self.walletnotify_dir)))
+        for tx_file in os.listdir(self.walletnotify_dir):
+            os.remove(os.path.join(self.walletnotify_dir, tx_file))
 
         self.log.info("test -walletnotify after rescan")
         # restart node to rescan to force wallet notifications
         self.restart_node(1)
         connect_nodes_bi(self.nodes[0], self.nodes[1])
 
-        wait_until(lambda: os.path.isfile(self.tx_filename) and os.stat(
-            self.tx_filename).st_size >= (block_count * 65), timeout=10)
+        wait_until(
+            lambda: len(
+                os.listdir(
+                    self.walletnotify_dir)) == block_count,
+            timeout=10)
 
-        # file content should equal the generated transaction hashes
+        # directory content should equal the generated transaction hashes
         txids_rpc = list(
             map(lambda t: t['txid'], self.nodes[1].listtransactions("*", block_count)))
-        with open(self.tx_filename, 'r', encoding="ascii") as f:
-            assert_equal(sorted(txids_rpc), sorted(l.strip()
-                                                   for l in f.read().splitlines()))
+        assert_equal(
+            sorted(txids_rpc), sorted(
+                os.listdir(
+                    self.walletnotify_dir)))
 
         # Create an invalid chain and ensure the node warns.
         self.log.info("test -alertnotify for forked chain")
@@ -91,12 +104,16 @@ def run_test(self):
         self.nodes[0].invalidateblock(invalid_block)
 
         # Give bitcoind 10 seconds to write the alert notification
-        wait_until(lambda: os.path.isfile(self.alert_filename) and
-                   os.path.getsize(self.alert_filename), timeout=10)
+        wait_until(lambda: len(os.listdir(self.alertnotify_dir)), timeout=10)
+
+        # The notification command is unable to properly handle the spaces on
+        # windows. Skip the content check in this case.
+        if os.name != 'nt':
+            assert FORK_WARNING_MESSAGE.format(
+                fork_block) in os.listdir(self.alertnotify_dir)
 
-        self.log.info(self.alert_filename)
-        with open(self.alert_filename, 'r', encoding='utf8') as f:
-            assert_equal(f.read(), (FORK_WARNING_MESSAGE.format(fork_block)))
+        for notify_file in os.listdir(self.alertnotify_dir):
+            os.remove(os.path.join(self.alertnotify_dir, notify_file))
 
 
 if __name__ == '__main__':
```
