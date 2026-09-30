# [?] Fix reentrancy vulnerability in example Crowfund.refund() (#2739)

## Summary
Severity: Unknown
Chain: Vyper
Component: vyperlang/vyper
Published: 2022-04-01
Source: https://github.com/vyperlang/vyper/commit/7f7379b89857c630e8ddca4e8173d8bde391cd0a
Type: security-commit

## Details
Fix reentrancy vulnerability in example Crowfund.refund() (#2739)

* Fix reentrancy vulnerability Crowfund.refund()

* Refactor crowdfund to his own folder

* Fix vulnerability REVERT on send() can prevent refund

* Fix one participation can participate multiple time

* Use 0 instead of empty; Put crowdfund outside of  folder

Co-authored-by: hitsuzen <hitsuzen@mail.com>

## Patch
### examples/crowdfund.vy
```diff
@@ -1,18 +1,11 @@
 # Setup private variables (only callable from within the contract)
 
-struct Funder :
-  sender: address
-  value: uint256
-
-funders: HashMap[int128, Funder]
-nextFunderIndex: int128
+funders: HashMap[address, uint256]
 beneficiary: address
 deadline: public(uint256)
 goal: public(uint256)
-refundIndex: int128
 timelimit: public(uint256)
 
-
 # Setup global variables
 @external
 def __init__(_beneficiary: address, _goal: uint256, _timelimit: uint256):
@@ -21,18 +14,13 @@ def __init__(_beneficiary: address, _goal: uint256, _timelimit: uint256):
     self.timelimit = _timelimit
     self.goal = _goal
 
-
 # Participate in this crowdfunding campaign
 @external
 @payable
 def participate():
     assert block.timestamp < self.deadline, "deadline not met (yet)"
 
-    nfi: int128 = self.nextFunderIndex
-
-    self.funders[nfi] = Funder({sender: msg.sender, value: msg.value})
-    self.nextFunderIndex = nfi + 1
-
+    self.funders[msg.sender] += msg.value
 
 # Enough money was raised! Send funds to the beneficiary
 @external
@@ -42,20 +30,13 @@ def finalize():
 
     selfdestruct(self.beneficiary)
 
-# Not enough money was raised! Refund everyone (max 30 people at a time
-# to avoid gas limit issues)
+# Let participants withdraw their fund
 @external
 def refund():
     assert block.timestamp >= self.deadline and self.balance < self.goal
+    assert self.funders[msg.sender] > 0
 
-    ind: int128 = self.refundIndex
-
-    for i in range(ind, ind + 30):
-        if i >= self.nextFunderIndex:
-            self.refundIndex = self.nextFunderIndex
-            return
-
-        send(self.funders[i].sender, self.funders[i].value)
-        self.funders[i] = empty(Funder)
+    value: uint256 = self.funders[msg.sender]
+    self.funders[msg.sender] = 0
 
-    self.refundIndex = ind + 30
+    send(msg.sender, value)
```

### tests/examples/crowdfund/test_crowdfund_example.py
```diff
@@ -27,7 +27,7 @@ def test_crowdfund_example(c, w3):
     assert post_bal - pre_bal == 54
 
 
-def test_crowdfund_example2(c, w3):
+def test_crowdfund_example2(c, w3, assert_tx_failed):
     a0, a1, a2, a3, a4, a5, a6 = w3.eth.accounts[:7]
     c.participate(transact={"value": 1, "from": a3})
     c.participate(transact={"value": 2, "from": a4})
@@ -39,6 +39,11 @@ def test_crowdfund_example2(c, w3):
     # assert c.expired()
     # assert not c.reached()
     pre_bals = [w3.eth.get_balance(x) for x in [a3, a4, a5, a6]]
-    c.refund(transact={})
+    assert_tx_failed(lambda: c.refund(transact={"from": a0}))
+    c.refund(transact={"from": a3})
+    assert_tx_failed(lambda: c.refund(transact={"from": a3}))
+    c.refund(transact={"from": a4})
+    c.refund(transact={"from": a5})
+    c.refund(transact={"from": a6})
     post_bals = [w3.eth.get_balance(x) for x in [a3, a4, a5, a6]]
     assert [y - x for x, y in zip(pre_bals, post_bals)] == [1, 2, 3, 4]
```
