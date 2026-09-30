# [?] remove overflow protection, rely on built-in protection instead

## Summary
Severity: Unknown
Chain: Vyper
Component: vyperlang/vyper
Published: 2017-10-19
Source: https://github.com/vyperlang/vyper/commit/e2685d6fc74fdb06bf5401f11870e65887a52a75
Type: security-commit

## Details
remove overflow protection, rely on built-in protection instead

## Patch
### examples/tokens/ERC20_solidity_compatible/ERC20.v.py
```diff
@@ -16,22 +16,10 @@
 allowances: (num256[address])[address]
 num_issued: num256
 
-# Utility functions for overflow checking
-@constant
-def is_overflow_add(a : num256, b : num256) -> bool:
-    result = num256_add(a, b)
-    return num256_lt(result, a)
-
-@constant
-def is_overflow_sub(a : num256, b : num256) -> bool:
-    return num256_lt(a, b)
-
 @payable
 def deposit():
     _value = as_num256(msg.value)
     _sender = msg.sender
-    assert not self.is_overflow_add(self.balances[_sender], _value)
-    assert not self.is_overflow_add(self.num_issued, _value)
     self.balances[_sender] = num256_add(self.balances[_sender], _value)
     self.num_issued = num256_add(self.num_issued, _value)
     # Fire deposit event as transfer from 0x0
@@ -40,8 +28,7 @@ def deposit():
 def withdraw(_value : num256) -> bool:
     _sender = msg.sender
     # Make sure sufficient funds are present, op will not underflow supply
-    assert not self.is_overflow_sub(self.balances[_sender], _value)
-    assert not self.is_overflow_sub(self.num_issued, _value)
+    # implicitly through overflow protection
     self.balances[_sender] = num256_sub(self.balances[_sender], _value)
     self.num_issued = num256_sub(self.num_issued, _value)
     send(_sender, as_wei_value(as_num128(_value), wei))
@@ -59,8 +46,7 @@ def balanceOf(_owner : address) -> num256:
 
 def transfer(_to : address, _value : num256) -> bool:
     _sender = msg.sender
-    assert not self.is_overflow_add(self.balances[_to], _value)
-    assert not self.is_overflow_sub(self.balances[_sender], _value)
+    # Make sure sufficient funds are present implicitly through overflow protection
     self.balances[_sender] = num256_sub(self.balances[_sender], _value)
     self.balances[_to] = num256_add(self.balances[_to], _value)
     # Fire transfer event
@@ -70,9 +56,7 @@ def transfer(_to : address, _value : num256) -> bool:
 def transferFrom(_from : address, _to : address, _value : num256) -> bool:
     _sender = msg.sender
     allowance = self.allowances[_from][_sender]
-    assert not self.is_overflow_add(self.balances[_to], _value)
-    assert not self.is_overflow_sub(self.balances[_from], _value)
-    assert not self.is_overflow_sub(allowance, _value)
+    # Make sure sufficient funds/allowance are present implicitly through overflow protection
     self.balances[_from] = num256_sub(self.balances[_from], _value)
     self.balances[_to] = num256_add(self.balances[_to], _value)
     self.allowances[_from][_sender] = num256_sub(allowance, _value)
```

### tests/examples/tokens/ERC20_solidity_compatible/test/erc20_tests_1.py
```diff
@@ -349,11 +349,6 @@ def setUpClass(cls):
     def setUp(self):
         super().setUp()
 
-    def test_internal_payability(self):
-        # Assert that contract-specific functions are nonpayable
-        self.assert_tx_failed(lambda :self.c.is_overflow_add(0, 0, value=2, sender=self.t.k1))
-        self.assert_tx_failed(lambda :self.c.is_overflow_sub(0, 0, value=2, sender=self.t.k1))
-
     def test_bad_transfer(self):
         # Ensure transfer fails if it would otherwise overflow balance
         # (bad contract is used or overflow checks on total supply would fail)
```
