# [?] Language Server: Fix hover crashes on invalid parameters

## Summary
Severity: Unknown
Chain: Solidity
Component: argotorg/solidity
Published: 2025-04-04
Source: https://github.com/argotorg/solidity/commit/e13c612202823d158e845df4435e405fd1576dea
Type: security-commit

## Details
Language Server: Fix hover crashes on invalid parameters

When `textDocument/hover` gets an out-of-range request

## Patch
### libsolidity/lsp/DocumentHoverHandler.cpp
```diff
@@ -59,6 +59,11 @@ void DocumentHoverHandler::operator()(MessageID _id, Json const& _args)
 {
 	auto const [sourceUnitName, lineColumn] = HandlerBase(*this).extractSourceUnitNameAndLineColumn(_args);
 	auto const [sourceNode, sourceOffset] = m_server.astNodeAndOffsetAtSourceLocation(sourceUnitName, lineColumn);
+	if (!sourceNode)
+	{
+		client().reply(_id, Json());
+		return;
+	}
 
 	MarkdownBuilder markdown;
 	auto rangeToHighlight = toRange(sourceNode->location());
```
