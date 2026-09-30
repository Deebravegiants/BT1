# [?] Fix reentrance test (#1757)

## Summary
Severity: Unknown
Chain: Conflux
Component: Conflux-Chain/conflux-rust
Published: 2020-08-07
Source: https://github.com/Conflux-Chain/conflux-rust/commit/08fe4e6cd6382b251ce579e440938b05953191cc
Type: security-commit

## Details
Fix reentrance test (#1757)

## Patch
### tests/contracts/reentrancy.sol
```diff
@@ -13,7 +13,8 @@ contract Reentrance {
 
     function withdrawBalance() public {
         uint x = balances[msg.sender];
-        msg.sender.call.value(x)("");
+        (bool success, ) = msg.sender.call.value(x)("");
+        require(success, "Fails to withdraw by callback.");
         balances[msg.sender] = 0;
     }
 }
```

### tests/reentrancy_test.py
```diff
@@ -177,6 +177,12 @@ def run_test(self):
         assert_greater_than_or_equal(user2_balance_after_deposit, 899999999999999999999999900000000)
         contract_balance = parse_as_int(self.nodes[0].cfx_getBalance(contract_addr))
         assert_equal(contract_balance, 2 * 10 ** 18)
+        user2_balance_in_contract = RpcClient(self.nodes[0]).call(
+            contract_addr,
+            self.buggy_contract.functions.balanceOf(Web3.toChecksumAddress(exploit_addr)).buildTransaction(
+                {"from":user2_addr_hex, "to":contract_addr, "gas":int_to_hex(CONTRACT_DEFAULT_GAS), "gasPrice":int_to_hex(1), "chainId":0}
+            )["data"])
+        assert_equal(parse_as_int(user2_balance_in_contract), 10 ** 18)
 
         transaction = self.call_contract_function(self.exploit_contract, "launch_attack", [], user2, 0,
                                                   exploit_addr, True, True, storage_limit=128)
@@ -186,16 +192,13 @@ def run_test(self):
         user1_balance = parse_as_int(self.nodes[0].cfx_getBalance(user1_addr_hex))
         assert_greater_than_or_equal(user1_balance, 899999999999999999999999950000000)
         contract_balance = parse_as_int(self.nodes[0].cfx_getBalance(contract_addr))
+        assert_equal(contract_balance, 2 * 10 ** 18)
         user2_balance_in_contract = RpcClient(self.nodes[0]).call(
             contract_addr,
-            self.buggy_contract.functions.balanceOf(Web3.toChecksumAddress(user2_addr_hex)).buildTransaction(
+            self.buggy_contract.functions.balanceOf(Web3.toChecksumAddress(exploit_addr)).buildTransaction(
                 {"from":user2_addr_hex, "to":contract_addr, "gas":int_to_hex(CONTRACT_DEFAULT_GAS), "gasPrice":int_to_hex(1), "chainId":0}
             )["data"])
-        assert_equal(contract_balance, 2 * 10 ** 18)
-        # FIXME: this assertion fails.
-        # assert_equal(parse_as_int(user2_balance_in_contract), 10 ** 18)
-        # FIXME: Because the balances[user2] becomes 0 due to the bug, we have to add one more storage refund
-        user2_refund_upper_bound += 10 ** 18 // 16
+        assert_equal(parse_as_int(user2_balance_in_contract), 10 ** 18)
         self.log.debug("user2 balance in contract %s" % user2_balance_in_contract)
         user2_balance_after_contract_destruct = parse_as_int(self.nodes[0].cfx_getBalance(user2_addr_hex))
         self.log.debug("user2 balance after contract destruct %s" % user2_balance_after_contract_destruct)
```
