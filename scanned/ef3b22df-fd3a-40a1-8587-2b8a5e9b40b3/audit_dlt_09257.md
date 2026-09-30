# [?] Fix out-of-range compiler crash for nested tuple assignment involving

## Summary
Severity: Unknown
Chain: Solidity
Component: argotorg/solidity
Published: 2022-07-16
Source: https://github.com/argotorg/solidity/commit/a9e03f5e4a19d4c70af7c28f5cea4bc4ee066ff2
Type: security-commit

## Details
Fix out-of-range compiler crash for nested tuple assignment involving
outer unary tuple

## Patch
### Changelog.md
```diff
@@ -14,6 +14,7 @@ Bugfixes:
  * Commandline Interface: Disallow the following options outside of the compiler mode: ``--via-ir``,``--metadata-literal``, ``--metadata-hash``, ``--model-checker-show-unproved``, ``--model-checker-div-mod-no-slacks``, ``--model-checker-engine``, ``--model-checker-invariants``, ``--model-checker-solvers``, ``--model-checker-timeout``, ``--model-checker-contracts``, ``--model-checker-targets``.
  * Type Checker: Fix null dereference in `abi.encodeCall` type checking of free function.
  * Type Checker: Fix compiler crash when `abi.encodeCall` received a tuple expression instead of an inline tuple.
+ * Type Checker: Fix compiler crash on tuple assignments involving certain patterns with unary tuples on the left-hand side.
 
 
 ### 0.8.15 (2022-06-15)
```

### libsolidity/analysis/TypeChecker.cpp
```diff
@@ -112,8 +112,9 @@ void TypeChecker::checkDoubleStorageAssignment(Assignment const& _assignment)
 	size_t storageByteAccesses = 0;
 	auto count = [&](TupleExpression const& _lhs, TupleType const& _rhs, auto _recurse) -> void {
 		TupleType const& lhsType = dynamic_cast<TupleType const&>(*type(_lhs));
+		TupleExpression const* lhsResolved = dynamic_cast<TupleExpression const*>(resolveOuterUnaryTuples(&_lhs));
 
-		if (lhsType.components().size() != _rhs.components().size())
+		if (lhsType.components().size() != _rhs.components().size() || lhsResolved->components().size() != _rhs.components().size())
 		{
 			solAssert(m_errorReporter.hasErrors(), "");
 			return;
@@ -134,7 +135,7 @@ void TypeChecker::checkDoubleStorageAssignment(Assignment const& _assignment)
 			{
 				if (bytesType && bytesType->numBytes() == 1)
 				{
-					if (FunctionCall const* lhsCall = dynamic_cast<FunctionCall const*>(resolveOuterUnaryTuples(_lhs.components().at(index).get())))
+					if (FunctionCall const* lhsCall = dynamic_cast<FunctionCall const*>(resolveOuterUnaryTuples(lhsResolved->components().at(index).get())))
 					{
 						FunctionType const& callType = dynamic_cast<FunctionType const&>(*type(lhsCall->expression()));
 						if (callType.kind() == FunctionType::Kind::ArrayPush)
@@ -147,7 +148,7 @@ void TypeChecker::checkDoubleStorageAssignment(Assignment const& _assignment)
 							}
 						}
 					}
-					else if (IndexAccess const* indexAccess = dynamic_cast<IndexAccess const*>(resolveOuterUnaryTuples(_lhs.components().at(index).get())))
+					else if (IndexAccess const* indexAccess = dynamic_cast<IndexAccess const*>(resolveOuterUnaryTuples(lhsResolved->components().at(index).get())))
 					{
 						if (ArrayType const* arrayType = dynamic_cast<ArrayType const*>(type(indexAccess->baseExpression())))
 							if (arrayType->isByteArray() && arrayType->dataStoredIn(DataLocation::Storage))
@@ -156,7 +157,7 @@ void TypeChecker::checkDoubleStorageAssignment(Assignment const& _assignment)
 				}
 			}
 			else if (TupleType const* tupleType = dynamic_cast<TupleType const*>(componentType))
-				if (auto const* lhsNested = dynamic_cast<TupleExpression const*>(_lhs.components().at(index).get()))
+				if (auto const* lhsNested = dynamic_cast<TupleExpression const*>(lhsResolved->components().at(index).get()))
 					if (auto const* rhsNestedType = dynamic_cast<TupleType const*>(_rhs.components().at(index)))
 						_recurse(
 							*lhsNested,
```

### test/libsolidity/syntaxTests/tupleAssignments/empty_tuple_assignment.sol
```diff
@@ -0,0 +1,35 @@
+function f() pure {
+    ((, ())) = (1, 3);
+}
+
+function g() pure {
+    ((, ((, ())))) = (1, 3);
+}
+
+function t() pure returns (int, int) {
+    return (4, 5);
+}
+
+function h() pure {
+    ((, ())) = t();
+}
+
+function ff() pure {
+    ((((, ())) , )) = ((1, 2), 3);
+}
+
+function fg() pure {
+    (((, ())) , ) = ((1, 2), 3);
+}
+
+// ----
+// TypeError 5547: (28-30): Empty tuple on the left hand side.
+// TypeError 7407: (35-41): Type tuple(int_const 1,int_const 3) is not implicitly convertible to expected type tuple(,tuple()).
+// TypeError 5547: (78-80): Empty tuple on the left hand side.
+// TypeError 7407: (87-93): Type tuple(int_const 1,int_const 3) is not implicitly convertible to expected type tuple(,tuple(,tuple())).
+// TypeError 5547: (187-189): Empty tuple on the left hand side.
+// TypeError 7407: (194-197): Type tuple(int256,int256) is not implicitly convertible to expected type tuple(,tuple()).
+// TypeError 5547: (233-235): Empty tuple on the left hand side.
+// TypeError 7407: (245-256): Type tuple(tuple(int_const 1,int_const 2),int_const 3) is not implicitly convertible to expected type tuple(tuple(,tuple()),).
+// TypeError 5547: (291-293): Empty tuple on the left hand side.
+// TypeError 7407: (302-313): Type tuple(tuple(int_const 1,int_const 2),int_const 3) is not implicitly convertible to expected type tuple(tuple(,tuple()),).
```

### test/libsolidity/syntaxTests/tupleAssignments/fixed_byte_array_assignment_in_tuple.sol
```diff
@@ -0,0 +1,7 @@
+contract A {
+    function f() pure public {
+        bytes1 b;
+        bytes1 a;
+        (((, , b))) = (1, 2, a);
+    }
+}
```
