# [?] Prevent crash when translating yul->ewasm with @use-src annotations

## Summary
Severity: Unknown
Chain: Solidity
Component: argotorg/solidity
Published: 2021-10-26
Source: https://github.com/argotorg/solidity/commit/49b4e77d6ba14aafd701b6f149227b7d138824f3
Type: security-commit

## Details
Prevent crash when translating yul->ewasm with @use-src annotations

## Patch
### Changelog.md
```diff
@@ -7,6 +7,7 @@ Compiler Features:
 
 
 Bugfixes:
+ * Code Generator: Fix a crash when using ``@use-src`` and compiling from Yul to ewasm.
 
 
 ### 0.8.10 (2021-11-09)
```

### libyul/backends/wasm/EVMToEwasmTranslator.cpp
```diff
@@ -137,7 +137,11 @@ void EVMToEwasmTranslator::parsePolyfill()
 			string(solidity::yul::wasm::polyfill::Logical) +
 			string(solidity::yul::wasm::polyfill::Memory) +
 		"}", "");
-	m_polyfill = Parser(errorReporter, WasmDialect::instance()).parse(charStream);
+
+	// Passing an empty SourceLocation() here is a workaround to prevent a crash
+	// when compiling from yul->ewasm. We're stripping nativeLocation and
+	// originLocation from the AST (but we only really need to strip nativeLocation)
+	m_polyfill = Parser(errorReporter, WasmDialect::instance(), langutil::SourceLocation()).parse(charStream);
 	if (!errors.empty())
 	{
 		string message;
```

### test/cmdlineTests/yul_to_wasm_source_location_crash/args
```diff
@@ -0,0 +1 @@
+--strict-assembly --yul-dialect evm --machine ewasm --optimize --ewasm-ir
```

### test/cmdlineTests/yul_to_wasm_source_location_crash/err
```diff
@@ -0,0 +1 @@
+Warning: Yul is still experimental. Please use the output with care.
```

### test/cmdlineTests/yul_to_wasm_source_location_crash/input.yul
```diff
@@ -0,0 +1,4 @@
+/// @use-src 0:"test.sol"
+object "C" {
+    code { sstore(0,0) }
+}
```

### test/cmdlineTests/yul_to_wasm_source_location_crash/output
```diff
@@ -0,0 +1,34 @@
+
+======= yul_to_wasm_source_location_crash/input.yul (Ewasm) =======
+
+==========================
+
+Translated source:
+/// @use-src 0:"test.sol"
+object "C" {
+    code {
+        function main()
+        {
+            let hi := i64.shl(i64.extend_i32_u(bswap32(i32.wrap_i64(0))), 32)
+            let y := i64.or(hi, i64.extend_i32_u(bswap32(i32.wrap_i64(i64.shr_u(0, 32)))))
+            i64.store(0:i32, y)
+            i64.store(i32.add(0:i32, 8:i32), y)
+            i64.store(i32.add(0:i32, 16:i32), y)
+            i64.store(i32.add(0:i32, 24:i32), y)
+            i64.store(32:i32, y)
+            i64.store(i32.add(32:i32, 8:i32), y)
+            i64.store(i32.add(32:i32, 16:i32), y)
+            i64.store(i32.add(32:i32, 24:i32), y)
+            eth.storageStore(0:i32, 32:i32)
+        }
+        function bswap16(x:i32) -> y:i32
+        {
+            y := i32.or(i32.and(i32.shl(x, 8:i32), 0xff00:i32), i32.and(i32.shr_u(x, 8:i32), 0xff:i32))
+        }
+        function bswap32(x:i32) -> y:i32
+        {
+            let hi:i32 := i32.shl(bswap16(x), 16:i32)
+            y := i32.or(hi, bswap16(i32.shr_u(x, 16:i32)))
+        }
+    }
+}
```
