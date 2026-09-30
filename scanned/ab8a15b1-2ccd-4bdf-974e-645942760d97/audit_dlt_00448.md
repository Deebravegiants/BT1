# [?] [pallet-revive] fix exp overflow (#9991)

## Summary
Severity: Unknown
Chain: Polkadot
Component: paritytech/polkadot-sdk
Published: 2025-10-10
Source: https://github.com/paritytech/polkadot-sdk/commit/bd5dba9595e4d5c5d7d043e3db3452c5754150b1
Type: security-commit

## Details
[pallet-revive] fix exp overflow (#9991)

Update arithmetic tests, and fix potential overflow

---------

Co-authored-by: cmd[bot] <41898282+github-actions[bot]@users.noreply.github.com>
Co-authored-by: xermicus <cyrill@parity.io>

## Patch
### prdoc/pr_9991.prdoc
```diff
@@ -0,0 +1,9 @@
+title: '[pallet-revive] fix exp overflow'
+doc:
+- audience: Runtime Dev
+  description: Update arithmetic tests, and fix potential overflow
+crates:
+- name: pallet-revive-fixtures
+  bump: patch
+- name: pallet-revive
+  bump: patch
```

### substrate/frame/revive/fixtures/contracts/Arithmetic.sol
```diff
@@ -2,41 +2,120 @@
 pragma solidity ^0.8.0;
 
 contract Arithmetic {
+    // We don't run the optimizer to avoid constant folding
     function testArithmetic() public {
         // ADD tests
-        require(20 + 22 == 42, "ADD basic");
+        uint256 addResult;
+        assembly {
+            addResult := add(20, 22)
+        }
+        require(addResult == 42, "ADD basic");
 
         // SUB tests
-        require(42 - 20 == 22, "SUB basic");
+        uint256 subResult;
+        assembly {
+            subResult := sub(42, 20)
+        }
+        require(subResult == 22, "SUB basic");
 
         // MUL tests
-        require(20 * 22 == 440, "MUL basic");
+        uint256 mulResult;
+        assembly {
+            mulResult := mul(20, 22)
+        }
+        require(mulResult == 440, "MUL basic");
 
         // DIV tests
-        require(100 / 5 == 20, "DIV basic");
+        uint256 divResult;
+        assembly {
+            divResult := div(100, 5)
+        }
+        require(divResult == 20, "DIV basic");
 
         // SDIV tests
-        require(int256(-100) / 5 == -20, "SDIV neg/pos");
-        require(int256(100) / -5 == -20, "SDIV pos/neg");
-        require(int256(-100) / -5 == 20, "SDIV neg/neg");
+        int256 sdivResult1;
+        assembly {
+            sdivResult1 := sdiv(sub(0, 100), 5)
+        }
+        require(sdivResult1 == -20, "SDIV neg/pos");
+
+        int256 sdivResult2;
+        assembly {
+            sdivResult2 := sdiv(100, sub(0, 5))
+        }
+        require(sdivResult2 == -20, "SDIV pos/neg");
+
+        int256 sdivResult3;
+        assembly {
+            sdivResult3 := sdiv(sub(0, 100), sub(0, 5))
+        }
+        require(sdivResult3 == 20, "SDIV neg/neg");
 
         // REM/MOD tests
-        require(100 % 7 == 2, "REM basic");
+        uint256 modResult;
+        assembly {
+            modResult := mod(100, 7)
+        }
+        require(modResult == 2, "REM basic");
 
         // SMOD tests
-        require(int256(-100) % 7 == -2, "SMOD neg dividend");
-        require(int256(100) % -7 == 2, "SMOD neg divisor");
+        int256 smodResult1;
+        assembly {
+            smodResult1 := smod(sub(0, 100), 7)
+        }
+        require(smodResult1 == -2, "SMOD neg dividend");
+
+        int256 smodResult2;
+        assembly {
+            smodResult2 := smod(100, sub(0, 7))
+        }
+        require(smodResult2 == 2, "SMOD neg divisor");
 
         // ADDMOD tests
-        require((10 + 15) % 7 == 4, "ADDMOD basic");
+        uint256 addmodResult;
+        assembly {
+            addmodResult := addmod(10, 15, 7)
+        }
+        require(addmodResult == 4, "ADDMOD basic");
 
         // MULMOD tests
-        require((10 * 15) % 7 == 3, "MULMOD basic");
+        uint256 mulmodResult;
+        assembly {
+            mulmodResult := mulmod(10, 15, 7)
+        }
+        require(mulmodResult == 3, "MULMOD basic");
 
         // EXP tests
-        require(2 ** 3 == 8, "EXP basic");
-        require(10 ** 0 == 1, "EXP zero exponent");
-        require(0 ** 5 == 0, "EXP zero base");
+        uint256 expResult1;
+        assembly {
+            expResult1 := exp(2, 3)
+        }
+        require(expResult1 == 8, "EXP basic");
+
+        uint256 expResult2;
+        assembly {
+            expResult2 := exp(10, 0)
+        }
+        require(expResult2 == 1, "EXP zero exponent");
+
+        uint256 expResult3;
+        assembly {
+            expResult3 := exp(0, 5)
+        }
+        require(expResult3 == 0, "EXP zero base");
+
+        // EXP overflow test: 2^256 mod 2^256 = 0
+        uint256 expResult;
+        assembly {
+            expResult := exp(2, 256)
+        }
+        require(expResult == 0, "EXP overflow");
+
+        // EXP test: 2^255 should not overflow
+        assembly {
+            expResult := exp(2, 255)
+        }
+        require(expResult == (1 << 255), "EXP 2^255");
 
         // SIGNEXTEND tests
         uint256 result1;
```

### substrate/frame/revive/src/vm/evm/instructions/arithmetic.rs
```diff
@@ -122,7 +122,7 @@ pub fn exp<E: Ext>(interpreter: &mut Interpreter<E>) -> ControlFlow<Halt> {
 		return ControlFlow::Break(Error::<E::T>::OutOfGas.into());
 	};
 	interpreter.ext.charge_or_halt(EVMGas(gas_cost))?;
-	*op2 = op1.pow(*op2);
+	*op2 = op1.overflowing_pow(*op2).0;
 	ControlFlow::Continue(())
 }
 
```

### substrate/frame/revive/src/vm/evm/instructions/bitwise.rs
```diff
@@ -147,7 +147,7 @@ pub fn byte<E: Ext>(interpreter: &mut Interpreter<E>) -> ControlFlow<Halt> {
 	interpreter.ext.charge_or_halt(EVMGas(VERYLOW))?;
 	let ([op1], op2) = interpreter.stack.popn_top()?;
 
-	let o1 = op1.as_usize();
+	let o1 = as_usize_saturated(op1);
 	*op2 = if o1 < 32 {
 		// `31 - o1` because `byte` returns LE, while we want BE
 		U256::from(op2.byte(31 - o1))
```
