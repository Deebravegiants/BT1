# [?] Merge pull request #14374 from ethereum/fix-non-deterministic-ir-function-generation-order

## Summary
Severity: Unknown
Chain: Solidity
Component: argotorg/solidity
Published: 2023-07-13
Source: https://github.com/argotorg/solidity/commit/3fc2eadbdb9ac5111eac97feb149fad9746dfbf2
Type: security-commit

## Details
Merge pull request #14374 from ethereum/fix-non-deterministic-ir-function-generation-order

Fix undefined order of functions when generating code for index expressions

## Patch
### Changelog.md
```diff
@@ -17,6 +17,7 @@ Compiler Features:
 
 
 Bugfixes:
+ * Code Generator: Fix not entirely deterministic order of functions in unoptimized Yul output. The choice of C++ compiler in some cases would result in different (but equivalent) bytecode (especially from native binaries vs emscripten binaries)
  * Commandline Interface: Fix internal error when using ``--stop-after parsing`` and requesting some of the outputs that require full analysis or compilation.
  * Commandline Interface: It is no longer possible to specify both ``--optimize-yul`` and ``--no-optimize-yul`` at the same time.
  * SMTChecker: Fix encoding of side-effects inside ``if`` and ``ternary conditional``statements in the BMC engine.
```

### libsolidity/codegen/ir/IRGeneratorForStatements.cpp
```diff
@@ -2295,13 +2295,13 @@ void IRGeneratorForStatements::endVisit(IndexAccess const& _indexAccess)
 			}
 			case DataLocation::Memory:
 			{
-				string const memAddress =
-					m_utils.memoryArrayIndexAccessFunction(arrayType) +
-					"(" +
-					IRVariable(_indexAccess.baseExpression()).part("mpos").name() +
-					", " +
-					expressionAsType(*_indexAccess.indexExpression(), *TypeProvider::uint256()) +
-					")";
+				string const indexAccessFunction = m_utils.memoryArrayIndexAccessFunction(arrayType);
+				string const baseRef = IRVariable(_indexAccess.baseExpression()).part("mpos").name();
+				string const indexExpression = expressionAsType(
+					*_indexAccess.indexExpression(),
+					*TypeProvider::uint256()
+				);
+				string const memAddress = indexAccessFunction + "(" + baseRef + ", " + indexExpression + ")";
 
 				setLValue(_indexAccess, IRLValue{
 					*arrayType.baseType(),
@@ -2311,28 +2311,28 @@ void IRGeneratorForStatements::endVisit(IndexAccess const& _indexAccess)
 			}
 			case DataLocation::CallData:
 			{
-				string indexAccessFunction = m_utils.calldataArrayIndexAccessFunction(arrayType);
-				string const indexAccessFunctionCall =
-					indexAccessFunction +
-					"(" +
-					IRVariable(_indexAccess.baseExpression()).commaSeparatedList() +
-					", " +
-					expressionAsType(*_indexAccess.indexExpression(), *TypeProvider::uint256()) +
-					")";
+				string const indexAccessFunction = m_utils.calldataArrayIndexAccessFunction(arrayType);
+				string const baseRef = IRVariable(_indexAccess.baseExpression()).commaSeparatedList();
+				string const indexExpression = expressionAsType(
+					*_indexAccess.indexExpression(),
+					*TypeProvider::uint256()
+				);
+				string const calldataAddress = indexAccessFunction + "(" + baseRef + ", " + indexExpression + ")";
+
 				if (arrayType.isByteArrayOrString())
 					define(_indexAccess) <<
 						m_utils.cleanupFunction(*arrayType.baseType()) <<
 						"(calldataload(" <<
-						indexAccessFunctionCall <<
+						calldataAddress <<
 						"))\n";
 				else if (arrayType.baseType()->isValueType())
 					define(_indexAccess) <<
 						m_utils.readFromCalldata(*arrayType.baseType()) <<
 						"(" <<
-						indexAccessFunctionCall <<
+						calldataAddress <<
 						")\n";
 				else
-					define(_indexAccess) << indexAccessFunctionCall << "\n";
+					define(_indexAccess) << calldataAddress << "\n";
 				break;
 			}
 		}
```
