# [?] Merge pull request #12902 from a3d4/fix-msvc-debug-stack-crash

## Summary
Severity: Unknown
Chain: Solidity
Component: argotorg/solidity
Published: 2022-04-06
Source: https://github.com/argotorg/solidity/commit/31b548577994397f7f849e8dd005d9d7aaa48c76
Type: security-commit

## Details
Merge pull request #12902 from a3d4/fix-msvc-debug-stack-crash

Fix MSVC Debug crash

## Patch
### libyul/optimiser/StructuralSimplifier.cpp
```diff
@@ -93,26 +93,31 @@ void StructuralSimplifier::operator()(Block& _block)
 
 void StructuralSimplifier::simplify(std::vector<yul::Statement>& _statements)
 {
-	util::GenericVisitor visitor{
-		util::VisitorFallback<OptionalStatements>{},
-		[&](If& _ifStmt) -> OptionalStatements {
-			if (expressionAlwaysTrue(*_ifStmt.condition))
-				return {std::move(_ifStmt.body.statements)};
-			else if (expressionAlwaysFalse(*_ifStmt.condition))
-				return {vector<Statement>{}};
-			return {};
-		},
-		[&](Switch& _switchStmt) -> OptionalStatements {
-			if (std::optional<u256> const constExprVal = hasLiteralValue(*_switchStmt.expression))
-				return replaceConstArgSwitch(_switchStmt, constExprVal.value());
-			return {};
-		},
-		[&](ForLoop& _forLoop) -> OptionalStatements {
-			if (expressionAlwaysFalse(*_forLoop.condition))
-				return {std::move(_forLoop.pre.statements)};
-			return {};
-		}
+	// Explicit local variables ifLambda, switchLambda, forLoopLambda are created to avoid MSVC C++17 Debug test crash
+	// (Run-Time Check Failure #2 - Stack around the variable '....' was corrupted).
+	// As soon as the issue is fixed, this workaround can be removed.
+	auto ifLambda = [&](If& _ifStmt) -> OptionalStatements
+	{
+		if (expressionAlwaysTrue(*_ifStmt.condition))
+			return {std::move(_ifStmt.body.statements)};
+		else if (expressionAlwaysFalse(*_ifStmt.condition))
+			return {vector<Statement>{}};
+		return {};
+	};
+	auto switchLambda = [&](Switch& _switchStmt) -> OptionalStatements
+	{
+		if (std::optional<u256> const constExprVal = hasLiteralValue(*_switchStmt.expression))
+			return replaceConstArgSwitch(_switchStmt, constExprVal.value());
+		return {};
 	};
+	auto forLoopLambda = [&](ForLoop& _forLoop) -> OptionalStatements
+	{
+		if (expressionAlwaysFalse(*_forLoop.condition))
+			return {std::move(_forLoop.pre.statements)};
+		return {};
+	};
+
+	util::GenericVisitor visitor{util::VisitorFallback<OptionalStatements>{}, ifLambda, switchLambda, forLoopLambda};
 
 	util::iterateReplacing(
 		_statements,
```
