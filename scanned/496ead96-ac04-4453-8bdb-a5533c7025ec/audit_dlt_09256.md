# [?] Fix null dereference in using for directive when operator name is empty

## Summary
Severity: Unknown
Chain: Solidity
Component: argotorg/solidity
Published: 2023-04-17
Source: https://github.com/argotorg/solidity/commit/64f57ac3c7a46d8f442bfc89ed352c256bef25cf
Type: security-commit

## Details
Fix null dereference in using for directive when operator name is empty

## Patch
### libsolidity/parsing/Parser.cpp
```diff
@@ -995,11 +995,17 @@ ASTPointer<UsingForDirective> Parser::parseUsingDirective()
 				Token operator_ = m_scanner->currentToken();
 				if (!util::contains(userDefinableOperators, operator_))
 				{
+					string operatorName;
+					if (!m_scanner->currentLiteral().empty())
+						operatorName = m_scanner->currentLiteral();
+					else if (char const* tokenString = TokenTraits::toString(operator_))
+						operatorName = string(tokenString);
+
 					parserError(
 						4403_error,
 						fmt::format(
 							"Not a user-definable operator: {}. Only the following operators can be user-defined: {}",
-							(!m_scanner->currentLiteral().empty() ? m_scanner->currentLiteral() : string(TokenTraits::toString(operator_))),
+							operatorName,
 							util::joinHumanReadable(userDefinableOperators | ranges::views::transform([](Token _t) { return string{TokenTraits::toString(_t)}; }))
 						)
 					);
```

### test/libsolidity/syntaxTests/operators/userDefined/operator_parsing_operator_name_empty_string.sol
```diff
@@ -0,0 +1,7 @@
+using {f as ''} for uint;
+using {f as ""} for int;
+using {f as hex""} for address;
+// ----
+// ParserError 4403: (12-14): Not a user-definable operator: . Only the following operators can be user-defined: |, &, ^, ~, +, -, *, /, %, ==, !=, <, >, <=, >=
+// ParserError 4403: (38-40): Not a user-definable operator: . Only the following operators can be user-defined: |, &, ^, ~, +, -, *, /, %, ==, !=, <, >, <=, >=
+// ParserError 4403: (63-68): Not a user-definable operator: . Only the following operators can be user-defined: |, &, ^, ~, +, -, *, /, %, ==, !=, <, >, <=, >=
```
