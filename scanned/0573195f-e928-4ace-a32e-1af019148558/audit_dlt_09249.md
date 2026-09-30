# [?] SMTChecker: Fix crash on external function call wrapped in 1-tuple

## Summary
Severity: Unknown
Chain: Solidity
Component: argotorg/solidity
Published: 2025-02-03
Source: https://github.com/argotorg/solidity/commit/934716b68529dbea6dc09d066d6cc8806c4e1811
Type: security-commit

## Details
SMTChecker: Fix crash on external function call wrapped in 1-tuple

The function call needs to be unwrapped from within nested parentheses
to get the proper call expression.

## Patch
### Changelog.md
```diff
@@ -13,6 +13,7 @@ Compiler Features:
 Bugfixes:
  * General: Fix internal compiler error when requesting IR AST outputs for interfaces and abstract contracts.
  * SMTChecker: Fix SMT logic error when analyzing cross-contract getter call with BMC.
+ * SMTChecker: Fix SMT logic error when external call has extra effectless parentheses.
  * SMTChecker: Fix SMT logic error when initializing a fixed-sized-bytes array using string literals.
  * SMTChecker: Fix SMT logic error when translating invariants involving array store and select operations.
  * SMTChecker: Fix wrong encoding of string literals as arguments of ``ecrecover`` precompile.
```

### libsolidity/formal/SMTEncoder.cpp
```diff
@@ -2771,7 +2771,7 @@ TypePointers SMTEncoder::replaceUserTypes(TypePointers const& _types)
 
 std::pair<Expression const*, FunctionCallOptions const*> SMTEncoder::functionCallExpression(FunctionCall const& _funCall)
 {
-	Expression const* callExpr = &_funCall.expression();
+	Expression const* callExpr = innermostTuple(_funCall.expression());
 	auto const* callOptions = dynamic_cast<FunctionCallOptions const*>(callExpr);
 	if (callOptions)
 		callExpr = &callOptions->expression();
```

### test/libsolidity/smtCheckerTests/external_calls/external_call_extra_parentheses_1.sol
```diff
@@ -0,0 +1,9 @@
+contract C {
+	function f() external {}
+	function g() public {
+		(this.f)();
+	}
+}
+// ====
+// SMTEngine: chc
+// ----
```

### test/libsolidity/smtCheckerTests/external_calls/external_call_extra_parentheses_2.sol
```diff
@@ -0,0 +1,12 @@
+contract D {
+	function f() external {}
+}
+
+contract C {
+	function g(D d) public {
+		((d.f))();
+	}
+}
+// ====
+// SMTEngine: chc
+// ----
```
