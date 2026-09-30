# [?] Merge pull request #13205 from ethereum/fix-stack-overflow-importing-large-AST-json-file

## Summary
Severity: Unknown
Chain: Solidity
Component: argotorg/solidity
Published: 2022-07-05
Source: https://github.com/argotorg/solidity/commit/c8aed8c15008cdbab5ed08f4815d62bde849480b
Type: security-commit

## Details
Merge pull request #13205 from ethereum/fix-stack-overflow-importing-large-AST-json-file

Fix segmentation fault when  importing large AST from json file

## Patch
### liblangutil/CharStream.h
```diff
@@ -73,9 +73,15 @@ class CharStream
 	CharStream() = default;
 	CharStream(std::string _source, std::string _name):
 		m_source(std::move(_source)), m_name(std::move(_name)) {}
+	CharStream(std::string _source, std::string _name, bool _importedFromAST):
+		m_source(std::move(_source)),
+		m_name(std::move(_name)),
+		m_importedFromAST(_importedFromAST)
+	{ }
 
 	size_t position() const { return m_position; }
 	bool isPastEndOfInput(size_t _charsForward = 0) const { return (m_position + _charsForward) >= m_source.size(); }
+	bool isImportedFromAST() const { return m_importedFromAST; }
 
 	char get(size_t _charsForward = 0) const { return m_source[m_position + _charsForward]; }
 	char advanceAndGet(size_t _chars = 1);
@@ -138,6 +144,7 @@ class CharStream
 private:
 	std::string m_source;
 	std::string m_name;
+	bool m_importedFromAST{false};
 	size_t m_position{0};
 };
 
```

### libsolidity/interface/CompilerStack.cpp
```diff
@@ -404,7 +404,8 @@ void CompilerStack::importASTs(map<string, Json::Value> const& _sources)
 		source.ast = src.second;
 		source.charStream = make_shared<CharStream>(
 			util::jsonCompactPrint(m_sourceJsons[src.first]),
-			src.first
+			src.first,
+			true // imported from AST
 		);
 		m_sources[path] = move(source);
 	}
```

### libyul/AsmPrinter.cpp
```diff
@@ -278,7 +278,11 @@ string AsmPrinter::formatSourceLocation(
 	{
 		sourceIndex = to_string(_nameToSourceIndex.at(*_location.sourceName));
 
-		if (_debugInfoSelection.snippet && _soliditySourceProvider)
+		if (
+			_debugInfoSelection.snippet &&
+			_soliditySourceProvider &&
+			!_soliditySourceProvider->charStream(*_location.sourceName).isImportedFromAST()
+		)
 		{
 			solidityCodeSnippet = escapeAndQuoteString(
 				_soliditySourceProvider->charStream(*_location.sourceName).singleLineSnippet(_location)
```
