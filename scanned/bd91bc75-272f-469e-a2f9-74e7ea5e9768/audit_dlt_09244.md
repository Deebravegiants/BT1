# [?] Merge pull request #16876 from argotorg/fix-crash-on-parenthesized-custom-error-in-require

## Summary
Severity: Unknown
Chain: Solidity
Component: argotorg/solidity
Published: 2026-07-24
Source: https://github.com/argotorg/solidity/commit/96bdc54854a16664ac9dde32862c733ee419c89c
Type: security-commit

## Details
Merge pull request #16876 from argotorg/fix-crash-on-parenthesized-custom-error-in-require

Codegen: Fix ICE on parenthesized custom error construction in require statement

## Patch
### Changelog.md
```diff
@@ -6,6 +6,7 @@ Compiler Features:
 * SMTChecker: Emit a deprecation warning for the BMC engine.
 
 Bugfixes:
+* Code Generator: Fix ICE on parenthesized custom error construction in require statement.
 * Commandline Interface: Report proper error instead of ICE on non-hex mixed-case address value given via `--libraries`.
 
 
```

### libsolidity/codegen/ExpressionCompiler.cpp
```diff
@@ -1318,10 +1318,11 @@ bool ExpressionCompiler::visit(FunctionCall const& _functionCall)
 				if (magicType && magicType->kind() == MagicType::Kind::Error)
 				{
 					// Make sure that error constructor arguments are evaluated regardless of the require condition
-					auto const& errorConstructorCall = dynamic_cast<FunctionCall const&>(*arguments[1]);
-					errorConstructorCall.expression().accept(*this);
+					auto const errorConstructorCall = dynamic_cast<FunctionCall const*>(resolveOuterUnaryTuples(arguments[1].get()));
+					solAssert(errorConstructorCall);
+					errorConstructorCall->expression().accept(*this);
 					std::vector<Type const*> errorConstructorArgumentTypes{};
-					for (ASTPointer<Expression const> const& errorConstructorArgument: errorConstructorCall.sortedArguments())
+					for (ASTPointer<Expression const> const& errorConstructorArgument: errorConstructorCall->sortedArguments())
 					{
 						errorConstructorArgument->accept(*this);
 						errorConstructorArgumentTypes.push_back(errorConstructorArgument->annotation().type);
@@ -1336,14 +1337,14 @@ bool ExpressionCompiler::visit(FunctionCall const& _functionCall)
 					}
 					catch (StackTooDeepError const& _exception)
 					{
-						_exception << errinfo_sourceLocation(errorConstructorCall.location());
+						_exception << errinfo_sourceLocation(errorConstructorCall->location());
 						throw _exception;
 					}
 					// stack: <arg0> <arg1> ... <argN> <condition>
 					m_context << Instruction::ISZERO << Instruction::ISZERO;
 					AssemblyItem successBranchTag = m_context.appendConditionalJump();
 
-					auto const* errorDefinition = dynamic_cast<ErrorDefinition const*>(ASTNode::referencedDeclaration(errorConstructorCall.expression()));
+					auto const* errorDefinition = dynamic_cast<ErrorDefinition const*>(ASTNode::referencedDeclaration(errorConstructorCall->expression()));
 					solAssert(errorDefinition && errorDefinition->functionType(true));
 					utils().revertWithError(
 						errorDefinition->functionType(true)->externalSignature(),
```

### libsolidity/codegen/ir/IRGeneratorForStatements.cpp
```diff
@@ -1163,9 +1163,10 @@ void IRGeneratorForStatements::endVisit(FunctionCall const& _functionCall)
 		auto const* magicType = dynamic_cast<MagicType const*>(messageArgumentType);
 		if (magicType && magicType->kind() == MagicType::Kind::Error)
 		{
-			auto const& errorConstructorCall = dynamic_cast<FunctionCall const&>(*arguments[1]);
-			appendCode() << m_utils.requireWithErrorFunction(errorConstructorCall) << "(" <<IRVariable(*arguments[0]).name();
-			for (auto argument: errorConstructorCall.arguments())
+			auto const errorConstructorCall = dynamic_cast<FunctionCall const*>(resolveOuterUnaryTuples(arguments[1].get()));
+			solAssert(errorConstructorCall);
+			appendCode() << m_utils.requireWithErrorFunction(*errorConstructorCall) << "(" <<IRVariable(*arguments[0]).name();
+			for (auto argument: errorConstructorCall->arguments())
 				if (argument->annotation().type->sizeOnStack() > 0)
 					appendCode() << ", " << IRVariable(*argument).commaSeparatedList();
 			appendCode() << ")\n";
```

### test/libsolidity/semanticTests/errors/require_custom_error_can_be_parenthesized.sol
```diff
@@ -0,0 +1,11 @@
+// This could be a syntax test, but we want to check compilation with --via-ir as well.
+contract C {
+    error MyError(uint256);
+    function f() public pure returns (uint256)
+    {
+        require(false, (MyError(1)));
+        return 42;
+    }
+}
+// ----
+// f() -> FAILURE, hex"30b1b565", 1
```
