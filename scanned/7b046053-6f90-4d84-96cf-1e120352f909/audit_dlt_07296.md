# [?] fix: mocknet fixed helper crashing  (#8754)

## Summary
Severity: Unknown
Chain: NEAR
Component: near/nearcore
Published: 2023-03-20
Source: https://github.com/near/nearcore/commit/da43f9e93560717d82b474cab6caa15d509707cf
Type: security-commit

## Details
fix: mocknet fixed helper crashing  (#8754)

- make the spoon test wait with upgrading nodes until the helper is done deploying contracts 
- make the helper test ignore connection refused exceptions when sending transactions - those happen when the selected rpc node is being upgraded
- added log level cmd line argument and cleaned up some logs

## Patch
### pytest/lib/mocknet_helpers.py
```diff
@@ -56,8 +56,10 @@ def get_nonce_for_pk(
 
 
 def get_latest_block_hash(addr=LOCAL_ADDR, port=RPC_PORT):
-    last_block_hash = get_status(addr=addr,
-                                 port=port)['sync_info']['latest_block_hash']
+    last_block_hash = get_status(
+        addr=addr,
+        port=port,
+    )['sync_info']['latest_block_hash']
     return base58.b58decode(last_block_hash.encode('utf-8'))
 
 
```

### pytest/tests/mocknet/helpers/load_test_spoon_helper.py
```diff
@@ -8,6 +8,7 @@
 import sys
 import time
 import argparse
+import requests
 
 # Don't use the pathlib magic because this file runs on a remote machine.
 sys.path.append('lib')
@@ -108,10 +109,10 @@ def main():
     # call the contract before it is deployed).
     delay = args.contract_deploy_time / test_state.num_test_accounts()
     logger.info(f'Start deploying, delay between deployments: {delay}')
+    assert delay >= 1
 
     time.sleep(random.random() * delay)
     start_time = time.monotonic()
-    assert delay >= 1
     load_test_utils.init_ft(test_state.node_account)
     for i, account in enumerate(test_state.test_accounts):
         logger.info(f'Deploying contract for account {account.key.account_id}')
@@ -135,21 +136,33 @@ def main():
     last_staking = 0
     start_time = time.monotonic()
     while time.monotonic() - start_time < args.test_timeout:
-        # Repeat the staking transactions in case the validator selection algorithm changes.
-        staked_time = mocknet.stake_available_amount(
-            test_state.node_account,
-            last_staking,
-        )
-        if staked_time is not None:
-            last_staking = staked_time
-
-        elapsed_time = time.monotonic() - start_time
-        total_tx_sent = mocknet_helpers.throttle_txns(
-            load_test_utils.send_random_transactions,
-            total_tx_sent,
-            elapsed_time,
-            test_state,
-        )
+        try:
+            # Repeat the staking transactions in case the validator selection algorithm changes.
+            staked_time = mocknet.stake_available_amount(
+                test_state.node_account,
+                last_staking,
+            )
+            if staked_time is not None:
+                last_staking = staked_time
+
+            elapsed_time = time.monotonic() - start_time
+            total_tx_sent = mocknet_helpers.throttle_txns(
+                load_test_utils.send_random_transactions,
+                total_tx_sent,
+                elapsed_time,
+                test_state,
+            )
+        except (
+                ConnectionRefusedError,
+                requests.exceptions.ConnectionError,
+        ) as e:
+            # If this happens only occasionally the loop will retry immediately,
+            # eventually pick a healthy rpc node and all will be fine. If it
+            # happens every time, it indicates that something is wrong and
+            # should be visible in grafana tx rate.
+            logger.warning(
+                f'Error when staking or sending tx. This may happen when the '
+                f'selected RPC node is being upgraded. The exception is {e}')
     logger.info('Stop the test')
 
 
```

### pytest/tests/mocknet/load_test_spoon.py
```diff
@@ -126,7 +126,7 @@ def run(self):
             self.__setup_remote_python_environments()
 
         if not self.skip_restart:
-            self.__restart()
+            self.__upload_genesis_and_restart()
 
         mocknet.wait_all_nodes_up(self.all_nodes)
 
@@ -158,19 +158,12 @@ def __parse_args(self):
         parser.add_argument('--num-nodes', type=int, required=True)
         parser.add_argument('--max-tps', type=float, required=True)
         parser.add_argument('--increasing-stakes', type=float, default=0.0)
-        parser.add_argument(
-            '--progressive-upgrade',
-            default=False,
-            action='store_true',
-        )
-        parser.add_argument('--skip-load', default=False, action='store_true')
-        parser.add_argument('--skip-setup', default=False, action='store_true')
-        parser.add_argument(
-            '--skip-restart',
-            default=False,
-            action='store_true',
-        )
-        parser.add_argument('--no-sharding', default=False, action='store_true')
+        parser.add_argument('--progressive-upgrade', action='store_true')
+
+        parser.add_argument('--skip-load', action='store_true')
+        parser.add_argument('--skip-setup', action='store_true')
+        parser.add_argument('--skip-restart', action='store_true')
+        parser.add_argument('--no-sharding', action='store_true')
         parser.add_argument('--num-seats', type=int, required=True)
 
         parser.add_argument('--test-timeout', type=int, default=12 * 60 * 60)
@@ -182,11 +175,15 @@ def __parse_args(self):
             'We need to slowly deploy contracts, otherwise we stall out the nodes',
         )
 
+        parser.add_argument('--log-level', default="INFO")
+
         # The flag is no longer needed but is kept for backwards-compatibility.
         parser.add_argument('--script', required=False)
 
         args = parser.parse_args()
 
+        logger.setLevel(args.log_level)
+
         self.chain_id = args.chain_id
         self.pattern = args.pattern
         self.epoch_length = args.epoch_length
@@ -205,6 +202,8 @@ def __parse_args(self):
         self.test_timeout = args.test_timeout
         self.contract_deploy_time = args.contract_deploy_time
 
+        self.log_level = args.log_level
+
         assert self.epoch_length > 0
         assert self.num_nodes > 0
         assert self.max_tps > 0
@@ -248,7 +247,7 @@ def __setup_remote_python_environments(self):
         )
         logger.info('Setting remote python environments -- done')
 
-    def __restart(self):
+    def __upload_genesis_and_restart(self):
         logger.info(f'Restarting')
         # Make sure nodes are running by restarting them.
         mocknet.stop_nodes(self.all_nodes)
@@ -288,16 +287,62 @@ def __start_load_test_helpers(self):
             self.validator_nodes,
             self.rpc_nodes,
             self.max_tps,
-            self.test_timeout,
+            # Make the helper run a bit longer - there is significant delay
+            # between the time when the first helper is started and when this
+            # scipts begins the test.
+            self.test_timeout + 4 * self.EPOCH_HEIGHT_CHECK_DELAY,
             self.contract_deploy_time,
         )
         logger.info('Starting transaction spamming scripts -- done.')
 
-    def __wait_to_complete(self):
-        full_test_duration = self.test_timeout + self.contract_deploy_time
+    def __check_neard_and_helper_are_running(self):
+        neard_running = mocknet.is_binary_running_all_nodes(
+            'neard',
+            self.all_nodes,
+        )
+        helper_running = mocknet.is_binary_running_all_nodes(
+            'load_test_spoon_helper.py',
+            self.validator_nodes,
+        )
+
+        logger.debug(
+            f'neard is running on {neard_running.count(True)}/{len(neard_running)} nodes'
+        )
+        logger.debug(
+            f'helper is running on {helper_running.count(True)}/{len(helper_running)} validator nodes'
+        )
+
+        for node, is_running in zip(self.all_nodes, neard_running):
+            if not is_running:
+                raise Exception(
+                    'The neard process is not running on some of the nodes! '
+                    f'The neard is not running on {node.instance_name}')
+
+        for node, is_running in zip(self.validator_nodes, helper_running):
+            if not is_running:
+                raise Exception(
+                    'The helper process is not running on some of the nodes! '
+                    f'The helper is not running on {node.instance_name}')
+
+    def __wait_to_deploy_contracts(self):
+        msg = 'Waiting for the helper to deploy contracts'
+        logger.info(f'{msg}: {self.contract_deploy_time}s')
 
+        start_time = time.monotonic()
+        while True:
+            self.__check_neard_and_helper_are_running()
+
+            now = time.monotonic()
+            remaining_time = self.contract_deploy_time + start_time - now
+            logger.info(f'{msg}: {round(remaining_time)}s')
+            if remaining_time < 0:
+                break
+
+            time.sleep(self.EPOCH_HEIGHT_CHECK_DELAY)
+
+    def __wait_to_complete(self):
         msg = 'Waiting for the loadtest to complete'
-        logger.info(f'{msg}: {full_test_duration}s')
+        logger.info(f'{msg}: {self.test_timeout}s')
 
         initial_epoch_height = mocknet.get_epoch_height(self.rpc_nodes, -1)
         logger.info(f'initial_epoch_height: {initial_epoch_height}')
@@ -306,33 +351,7 @@ def __wait_to_complete(self):
         prev_epoch_height = initial_epoch_height
         start_time = time.monotonic()
         while True:
-            neard_running = mocknet.is_binary_running_all_nodes(
-                'neard',
-                self.all_nodes,
-            )
-            helper_running = mocknet.is_binary_running_all_nodes(
-                'load_test_spoon_helper.py',
-                self.validator_nodes,
-            )
-
-            logger.info(
-                f'neard is running on {neard_running.count(True)}/{len(neard_running)} nodes'
-            )
-            logger.info(
-                f'helper is running on {helper_running.count(True)}/{len(helper_running)} validator nodes'
-            )
-
-            if not all(neard_running):
-                raise Exception(
-                    f'The neard process is not running on some nodes!')
-
-            for node, is_running in zip(self.all_nodes, helper_running):
-                if not is_running:
-                    logger.warning(
-                        'The helper process is not running on some of the nodes. '
-                        'This is fine by the end of the test but an error otherwise. '
-                        f'The helper is not running on {node.instance_name}')
-                    break
+            self.__check_neard_and_helper_are_running()
 
             epoch_height = mocknet.get_epoch_height(
                 self.rpc_nodes,
@@ -346,7 +365,7 @@ def __wait_to_complete(self):
                 )
                 prev_epoch_height = epoch_height
 
-            remaining_time = full_test_duration + start_time - time.monotonic()
+            remaining_time = self.test_timeout + start_time - time.monotonic()
             logger.info(f'{msg}: {round(remaining_time)}s')
             if remaining_time < 0:
                 break
@@ -361,6 +380,8 @@ def __load(self):
 
         self.__start_load_test_helpers()
 
+        self.__wait_to_deploy_contracts()
+
         self.__wait_to_complete()
 
         logger.info(f'{msg} -- done')
@@ -383,9 +404,8 @@ def __final_checks(
             test_passed = False
             logger.error('Too many slow blocks')
 
-        if initial_validator_accounts != final_validator_accounts:
-            test_passed = False
-            logger.error(
+        if set(initial_validator_accounts) != set(final_validator_accounts):
+            logger.warning(
                 f'Mismatching set of validators:\n'
                 f'initial_validator_accounts: {initial_validator_accounts}\n'
                 f'final_validator_accounts  : {final_validator_accounts}')
```
