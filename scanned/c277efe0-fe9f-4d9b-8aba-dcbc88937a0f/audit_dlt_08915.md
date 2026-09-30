# [?] fix: stack overflow in sierra compiler

## Summary
Severity: Unknown
Chain: Starknet
Component: software-mansion/pathfinder
Published: 2023-07-10
Source: https://github.com/software-mansion/pathfinder/commit/233777a92a0437725c43de3381755eda5ebf70ec
Type: security-commit

## Details
fix: stack overflow in sierra compiler

## Patch
### CHANGELOG.md
```diff
@@ -11,6 +11,10 @@ and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0
 
 ## [0.6.6] - 2023-07-10
 
+### Fixed
+
+- stack overflow while compiling Sierra to CASM
+
 ## [0.6.5] - 2023-07-07
 
 ### Fixed
```

### Cargo.lock
```diff
@@ -846,10 +846,10 @@ dependencies = [
 
 [[package]]
 name = "cairo-lang-casm"
-version = "2.0.0-rc6"
-source = "git+https://github.com/starkware-libs/cairo?tag=v2.0.0-rc6#54bd0e668e92c6ae504bfa0f680e22b4c29be27d"
+version = "2.0.2"
+source = "git+https://github.com/starkware-libs/cairo?tag=v2.0.2#79b34bf9dabfb1a81937a79f155857f0592cccc0"
 dependencies = [
- "cairo-lang-utils 2.0.0-rc6",
+ "cairo-lang-utils 2.0.2",
  "indoc 2.0.1",
  "num-bigint 0.4.3",
  "num-traits 0.2.15",
@@ -911,22 +911,22 @@ dependencies = [
 
 [[package]]
 name = "cairo-lang-compiler"
-version = "2.0.0-rc6"
-source = "git+https://github.com/starkware-libs/cairo?tag=v2.0.0-rc6#54bd0e668e92c6ae504bfa0f680e22b4c29be27d"
+version = "2.0.2"
+source = "git+https://github.com/starkware-libs/cairo?tag=v2.0.2#79b34bf9dabfb1a81937a79f155857f0592cccc0"
 dependencies = [
  "anyhow",
- "cairo-lang-defs 2.0.0-rc6",
- "cairo-lang-diagnostics 2.0.0-rc6",
- "cairo-lang-filesystem 2.0.0-rc6",
- "cairo-lang-lowering 2.0.0-rc6",
- "cairo-lang-parser 2.0.0-rc6",
- "cairo-lang-plugins 2.0.0-rc6",
- "cairo-lang-project 2.0.0-rc6",
- "cairo-lang-semantic 2.0.0-rc6",
- "cairo-lang-sierra 2.0.0-rc6",
- "cairo-lang-sierra-generator 2.0.0-rc6",
- "cairo-lang-syntax 2.0.0-rc6",
- "cairo-lang-utils 2.0.0-rc6",
+ "cairo-lang-defs 2.0.2",
+ "cairo-lang-diagnostics 2.0.2",
+ "cairo-lang-filesystem 2.0.2",
+ "cairo-lang-lowering 2.0.2",
+ "cairo-lang-parser 2.0.2",
+ "cairo-lang-plugins 2.0.2",
+ "cairo-lang-project 2.0.2",
+ "cairo-lang-semantic 2.0.2",
+ "cairo-lang-sierra 2.0.2",
+ "cairo-lang-sierra-generator 2.0.2",
+ "cairo-lang-syntax 2.0.2",
+ "cairo-lang-utils 2.0.2",
  "log",
  "salsa",
  "smol_str 0.2.0",
@@ -945,10 +945,10 @@ source = "git+https://github.com/starkware-libs/cairo?tag=v1.0.0-rc0#05867c82de4
 
 [[package]]
 name = "cairo-lang-debug"
-version = "2.0.0-rc6"
-source = "git+https://github.com/starkware-libs/cairo?tag=v2.0.0-rc6#54bd0e668e92c6ae504bfa0f680e22b4c29be27d"
+version = "2.0.2"
+source = "git+https://github.com/starkware-libs/cairo?tag=v2.0.2#79b34bf9dabfb1a81937a79f155857f0592cccc0"
 dependencies = [
- "cairo-lang-utils 2.0.0-rc6",
+ "cairo-lang-utils 2.0.2",
 ]
 
 [[package]]
@@ -987,15 +987,15 @@ dependencies = [
 
 [[package]]
 name = "cairo-lang-defs"
-version = "2.0.0-rc6"
-source = "git+https://github.com/starkware-libs/cairo?tag=v2.0.0-rc6#54bd0e668e92c6ae504bfa0f680e22b4c29be27d"
-dependencies = [
- "cairo-lang-debug 2.0.0-rc6",
- "cairo-lang-diagnostics 2.0.0-rc6",
- "cairo-lang-filesystem 2.0.0-rc6",
- "cairo-lang-parser 2.0.0-rc6",
- "cairo-lang-syntax 2.0.0-rc6",
- "cairo-lang-utils 2.0.0-rc6",
+version = "2.0.2"
+source = "git+https://github.com/starkware-libs/cairo?tag=v2.0.2#79b34bf9dabfb1a81937a79f155857f0592cccc0"
+dependencies = [
+ "cairo-lang-debug 2.0.2",
+ "cairo-lang-diagnostics 2.0.2",
+ "cairo-lang-filesystem 2.0.2",
+ "cairo-lang-parser 2.0.2",
+ "cairo-lang-syntax 2.0.2",
+ "cairo-lang-utils 2.0.2",
  "indexmap",
  "itertools",
  "salsa",
@@ -1026,11 +1026,11 @@ dependencies = [
 
 [[package]]
 name = "cairo-lang-diagnostics"
-version = "2.0.0-rc6"
-source = "git+https://github.com/starkware-libs/cairo?tag=v2.0.0-rc6#54bd0e668e92c6ae504bfa0f680e22b4c29be27d"
+version = "2.0.2"
+source = "git+https://github.com/starkware-libs/cairo?tag=v2.0.2#79b34bf9dabfb1a81937a79f155857f0592cccc0"
 dependencies = [
- "cairo-lang-filesystem 2.0.0-rc6",
- "cairo-lang-utils 2.0.0-rc6",
+ "cairo-lang-filesystem 2.0.2",
+ "cairo-lang-utils 2.0.2",
  "itertools",
  "salsa",
 ]
@@ -1059,10 +1059,10 @@ dependencies = [
 
 [[package]]
 name = "cairo-lang-eq-solver"
-version = "2.0.0-rc6"
-source = "git+https://github.com/starkware-libs/cairo?tag=v2.0.0-rc6#54bd0e668e92c6ae504bfa0f680e22b4c29be27d"
+version = "2.0.2"
+source = "git+https://github.com/starkware-libs/cairo?tag=v2.0.2#79b34bf9dabfb1a81937a79f155857f0592cccc0"
 dependencies = [
- "cairo-lang-utils 2.0.0-rc6",
+ "cairo-lang-utils 2.0.2",
  "good_lp",
  "indexmap",
  "itertools",
@@ -1095,11 +1095,11 @@ dependencies = [
 
 [[package]]
 name = "cairo-lang-filesystem"
-version = "2.0.0-rc6"
-source = "git+https://github.com/starkware-libs/cairo?tag=v2.0.0-rc6#54bd0e668e92c6ae504bfa0f680e22b4c29be27d"
+version = "2.0.2"
+source = "git+https://github.com/starkware-libs/cairo?tag=v2.0.2#79b34bf9dabfb1a81937a79f155857f0592cccc0"
 dependencies = [
- "cairo-lang-debug 2.0.0-rc6",
- "cairo-lang-utils 2.0.0-rc6",
+ "cairo-lang-debug 2.0.2",
+ "cairo-lang-utils 2.0.2",
  "path-clean",
  "salsa",
  "serde",
@@ -1156,18 +1156,18 @@ dependencies = [
 
 [[package]]
 name = "cairo-lang-lowering"
-version = "2.0.0-rc6"
-source = "git+https://github.com/starkware-libs/cairo?tag=v2.0.0-rc6#54bd0e668e92c6ae504bfa0f680e22b4c29be27d"
-dependencies = [
- "cairo-lang-debug 2.0.0-rc6",
- "cairo-lang-defs 2.0.0-rc6",
- "cairo-lang-diagnostics 2.0.0-rc6",
- "cairo-lang-filesystem 2.0.0-rc6",
- "cairo-lang-parser 2.0.0-rc6",
- "cairo-lang-proc-macros 2.0.0-rc6",
- "cairo-lang-semantic 2.0.0-rc6",
- "cairo-lang-syntax 2.0.0-rc6",
- "cairo-lang-utils 2.0.0-rc6",
+version = "2.0.2"
+source = "git+https://github.com/starkware-libs/cairo?tag=v2.0.2#79b34bf9dabfb1a81937a79f155857f0592cccc0"
+dependencies = [
+ "cairo-lang-debug 2.0.2",
+ "cairo-lang-defs 2.0.2",
+ "cairo-lang-diagnostics 2.0.2",
+ "cairo-lang-filesystem 2.0.2",
+ "cairo-lang-parser 2.0.2",
+ "cairo-lang-proc-macros 2.0.2",
+ "cairo-lang-semantic 2.0.2",
+ "cairo-lang-syntax 2.0.2",
+ "cairo-lang-utils 2.0.2",
  "id-arena",
  "indexmap",
  "itertools",
@@ -1217,14 +1217,14 @@ dependencies = [
 
 [[package]]
 name = "cairo-lang-parser"
-version = "2.0.0-rc6"
-source = "git+https://github.com/starkware-libs/cairo?tag=v2.0.0-rc6#54bd0e668e92c6ae504bfa0f680e22b4c29be27d"
-dependencies = [
- "cairo-lang-diagnostics 2.0.0-rc6",
- "cairo-lang-filesystem 2.0.0-rc6",
- "cairo-lang-syntax 2.0.0-rc6",
- "cairo-lang-syntax-codegen 2.0.0-rc6",
- "cairo-lang-utils 2.0.0-rc6",
+version = "2.0.2"
+source = "git+https://github.com/starkware-libs/cairo?tag=v2.0.2#79b34bf9dabfb1a81937a79f155857f0592cccc0"
+dependencies = [
+ "cairo-lang-diagnostics 2.0.2",
+ "cairo-lang-filesystem 2.0.2",
+ "cairo-lang-syntax 2.0.2",
+ "cairo-lang-syntax-codegen 2.0.2",
+ "cairo-lang-utils 2.0.2",
  "colored",
  "itertools",
  "log",
@@ -1274,16 +1274,16 @@ dependencies = [
 
 [[package]]
 name = "cairo-lang-plugins"
-version = "2.0.0-rc6"
-source = "git+https://github.com/starkware-libs/cairo?tag=v2.0.0-rc6#54bd0e668e92c6ae504bfa0f680e22b4c29be27d"
-dependencies = [
- "cairo-lang-defs 2.0.0-rc6",
- "cairo-lang-diagnostics 2.0.0-rc6",
- "cairo-lang-filesystem 2.0.0-rc6",
- "cairo-lang-parser 2.0.0-rc6",
- "cairo-lang-semantic 2.0.0-rc6",
- "cairo-lang-syntax 2.0.0-rc6",
- "cairo-lang-utils 2.0.0-rc6",
+version = "2.0.2"
+source = "git+https://github.com/starkware-libs/cairo?tag=v2.0.2#79b34bf9dabfb1a81937a79f155857f0592cccc0"
+dependencies = [
+ "cairo-lang-defs 2.0.2",
+ "cairo-lang-diagnostics 2.0.2",
+ "cairo-lang-filesystem 2.0.2",
+ "cairo-lang-parser 2.0.2",
+ "cairo-lang-semantic 2.0.2",
+ "cairo-lang-syntax 2.0.2",
+ "cairo-lang-utils 2.0.2",
  "indoc 2.0.1",
  "itertools",
  "salsa",
@@ -1312,10 +1312,10 @@ dependencies = [
 
 [[package]]
 name = "cairo-lang-proc-macros"
-version = "2.0.0-rc6"
-source = "git+https://github.com/starkware-libs/cairo?tag=v2.0.0-rc6#54bd0e668e92c6ae504bfa0f680e22b4c29be27d"
+version = "2.0.2"
+source = "git+https://github.com/starkware-libs/cairo?tag=v2.0.2#79b34bf9dabfb1a81937a79f155857f0592cccc0"
 dependencies = [
- "cairo-lang-debug 2.0.0-rc6",
+ "cairo-lang-debug 2.0.2",
  "quote",
  "syn 1.0.109",
 ]
@@ -1346,11 +1346,11 @@ dependencies = [
 
 [[package]]
 name = "cairo-lang-project"
-version = "2.0.0-rc6"
-source = "git+https://github.com/starkware-libs/cairo?tag=v2.0.0-rc6#54bd0e668e92c6ae504bfa0f680e22b4c29be27d"
+version = "2.0.2"
+source = "git+https://github.com/starkware-libs/cairo?tag=v2.0.2#79b34bf9dabfb1a81937a79f155857f0592cccc0"
 dependencies = [
- "cairo-lang-filesystem 2.0.0-rc6",
- "cairo-lang-utils 2.0.0-rc6",
+ "cairo-lang-filesystem 2.0.2",
+ "cairo-lang-utils 2.0.2",
  "serde",
  "smol_str 0.2.0",
  "thiserror",
@@ -1405,17 +1405,17 @@ dependencies = [
 
 [[package]]
 name = "cairo-lang-semantic"
-version = "2.0.0-rc6"
-source = "git+https://github.com/starkware-libs/cairo?tag=v2.0.0-rc6#54bd0e668e92c6ae504bfa0f680e22b4c29be27d"
-dependencies = [
- "cairo-lang-debug 2.0.0-rc6",
- "cairo-lang-defs 2.0.0-rc6",
- "cairo-lang-diagnostics 2.0.0-rc6",
- "cairo-lang-filesystem 2.0.0-rc6",
- "cairo-lang-parser 2.0.0-rc6",
- "cairo-lang-proc-macros 2.0.0-rc6",
- "cairo-lang-syntax 2.0.0-rc6",
- "cairo-lang-utils 2.0.0-rc6",
+version = "2.0.2"
+source = "git+https://github.com/starkware-libs/cairo?tag=v2.0.2#79b34bf9dabfb1a81937a79f155857f0592cccc0"
+dependencies = [
+ "cairo-lang-debug 2.0.2",
+ "cairo-lang-defs 2.0.2",
+ "cairo-lang-diagnostics 2.0.2",
+ "cairo-lang-filesystem 2.0.2",
+ "cairo-lang-parser 2.0.2",
+ "cairo-lang-proc-macros 2.0.2",
+ "cairo-lang-syntax 2.0.2",
+ "cairo-lang-utils 2.0.2",
  "id-arena",
  "itertools",
  "log",
@@ -1471,10 +1471,10 @@ dependencies = [
 
 [[package]]
 name = "cairo-lang-sierra"
-version = "2.0.0-rc6"
-source = "git+https://github.com/starkware-libs/cairo?tag=v2.0.0-rc6#54bd0e668e92c6ae504bfa0f680e22b4c29be27d"
+version = "2.0.2"
+source = "git+https://github.com/starkware-libs/cairo?tag=v2.0.2#79b34bf9dabfb1a81937a79f155857f0592cccc0"
 dependencies = [
- "cairo-lang-utils 2.0.0-rc6",
+ "cairo-lang-utils 2.0.2",
  "const-fnv1a-hash",
  "convert_case",
  "derivative",
@@ -1517,12 +1517,12 @@ dependencies = [
 
 [[package]]
 name = "cairo-lang-sierra-ap-change"
-version = "2.0.0-rc6"
-source = "git+https://github.com/starkware-libs/cairo?tag=v2.0.0-rc6#54bd0e668e92c6ae504bfa0f680e22b4c29be27d"
+version = "2.0.2"
+source = "git+https://github.com/starkware-libs/cairo?tag=v2.0.2#79b34bf9dabfb1a81937a79f155857f0592cccc0"
 dependencies = [
- "cairo-lang-eq-solver 2.0.0-rc6",
- "cairo-lang-sierra 2.0.0-rc6",
- "cairo-lang-utils 2.0.0-rc6",
+ "cairo-lang-eq-solver 2.0.2",
+ "cairo-lang-sierra 2.0.2",
+ "cairo-lang-utils 2.0.2",
  "itertools",
  "thiserror",
 ]
@@ -1553,12 +1553,12 @@ dependencies = [
 
 [[package]]
 name = "cairo-lang-sierra-gas"
-version = "2.0.0-rc6"
-source = "git+https://github.com/starkware-libs/cairo?tag=v2.0.0-rc6#54bd0e668e92c6ae504bfa0f680e22b4c29be27d"
+version = "2.0.2"
+source = "git+https://github.com/starkware-libs/cairo?tag=v2.0.2#79b34bf9dabfb1a81937a79f155857f0592cccc0"
 dependencies = [
- "cairo-lang-eq-solver 2.0.0-rc6",
- "cairo-lang-sierra 2.0.0-rc6",
- "cairo-lang-utils 2.0.0-rc6",
+ "cairo-lang-eq-solver 2.0.2",
+ "cairo-lang-sierra 2.0.2",
+ "cairo-lang-utils 2.0.2",
  "itertools",
  "thiserror",
 ]
@@ -1615,21 +1615,21 @@ dependencies = [
 
 [[package]]
 name = "cairo-lang-sierra-generator"
-version = "2.0.0-rc6"
-source = "git+https://github.com/starkware-libs/cairo?tag=v2.0.0-rc6#54bd0e668e92c6ae504bfa0f680e22b4c29be27d"
-dependencies = [
- "cairo-lang-debug 2.0.0-rc6",
- "cairo-lang-defs 2.0.0-rc6",
- "cairo-lang-diagnostics 2.0.0-rc6",
- "cairo-lang-filesystem 2.0.0-rc6",
- "cairo-lang-lowering 2.0.0-rc6",
- "cairo-lang-parser 2.0.0-rc6",
- "cairo-lang-plugins 2.0.0-rc6",
- "cairo-lang-proc-macros 2.0.0-rc6",
- "cairo-lang-semantic 2.0.0-rc6",
- "cairo-lang-sierra 2.0.0-rc6",
- "cairo-lang-syntax 2.0.0-rc6",
- "cairo-lang-utils 2.0.0-rc6",
+version = "2.0.2"
+source = "git+https://github.com/starkware-libs/cairo?tag=v2.0.2#79b34bf9dabfb1a81937a79f155857f0592cccc0"
+dependencies = [
+ "cairo-lang-debug 2.0.2",
+ "cairo-lang-defs 2.0.2",
+ "cairo-lang-diagnostics 2.0.2",
+ "cairo-lang-filesystem 2.0.2",
+ "cairo-lang-lowering 2.0.2",
+ "cairo-lang-parser 2.0.2",
+ "cairo-lang-plugins 2.0.2",
+ "cairo-lang-proc-macros 2.0.2",
+ "cairo-lang-semantic 2.0.2",
+ "cairo-lang-sierra 2.0.2",
+ "cairo-lang-syntax 2.0.2",
+ "cairo-lang-utils 2.0.2",
  "id-arena",
  "indexmap",
  "itertools",
@@ -1684,16 +1684,16 @@ dependencies = [
 
 [[package]]
 name = "cairo-lang-sierra-to-casm"
-version = "2.0.0-rc6"
-source = "git+https://github.com/starkware-libs/cairo?tag=v2.0.0-rc6#54bd0e668e92c6ae504bfa0f680e22b4c29be27d"
+version = "2.0.2"
+source = "git+https://github.com/starkware-libs/cairo?tag=v2.0.2#79b34bf9dabfb1a81937a79f155857f0592cccc0"
 dependencies = [
  "assert_matches",
  "cairo-felt 0.6.1",
- "cairo-lang-casm 2.0.0-rc6",
- "cairo-lang-sierra 2.0.0-rc6",
- "cairo-lang-sierra-ap-change 2.0.0-rc6",
- "cairo-lang-sierra-gas 2.0.0-rc6",
- "cairo-lang-utils 2.0.0-rc6",
+ "cairo-lang-casm 2.0.2",
+ "cairo-lang-sierra 2.0.2",
+ "cairo-lang-sierra-ap-change 2.0.2",
+ "cairo-lang-sierra-gas 2.0.2",
+ "cairo-lang-utils 2.0.2",
  "indoc 2.0.1",
  "itertools",
  "log",
@@ -1783,27 +1783,27 @@ dependencies = [
 
 [[package]]
 name = "cairo-lang-starknet"
-version = "2.0.0-rc6"
-source = "git+https://github.com/starkware-libs/cairo?tag=v2.0.0-rc6#54bd0e668e92c6ae504bfa0f680e22b4c29be27d"
+version = "2.0.2"
+source = "git+https://github.com/starkware-libs/cairo?tag=v2.0.2#79b34bf9dabfb1a81937a79f155857f0592cccc0"
 dependencies = [
  "anyhow",
  "cairo-felt 0.6.1",
- "cairo-lang-casm 2.0.0-rc6",
- "cairo-lang-compiler 2.0.0-rc6",
- "cairo-lang-defs 2.0.0-rc6",
- "cairo-lang-diagnostics 2.0.0-rc6",
- "cairo-lang-filesystem 2.0.0-rc6",
- "cairo-lang-lowering 2.0.0-rc6",
- "cairo-lang-parser 2.0.0-rc6",
- "cairo-lang-plugins 2.0.0-rc6",
- "cairo-lang-semantic 2.0.0-rc6",
- "cairo-lang-sierra 2.0.0-rc6",
- "cairo-lang-sierra-ap-change 2.0.0-rc6",
- "cairo-lang-sierra-gas 2.0.0-rc6",
- "cairo-lang-sierra-generator 2.0.0-rc6",
- "cairo-lang-sierra-to-casm 2.0.0-rc6",
- "cairo-lang-syntax 2.0.0-rc6",
- "cairo-lang-utils 2.0.0-rc6",
+ "cairo-lang-casm 2.0.2",
+ "cairo-lang-compiler 2.0.2",
+ "cairo-lang-defs 2.0.2",
+ "cairo-lang-diagnostics 2.0.2",
+ "cairo-lang-filesystem 2.0.2",
+ "cairo-lang-lowering 2.0.2",
+ "cairo-lang-parser 2.0.2",
+ "cairo-lang-plugins 2.0.2",
+ "cairo-lang-semantic 2.0.2",
+ "cairo-lang-sierra 2.0.2",
+ "cairo-lang-sierra-ap-change 2.0.2",
+ "cairo-lang-sierra-gas 2.0.2",
+ "cairo-lang-sierra-generator 2.0.2",
+ "cairo-lang-sierra-to-casm 2.0.2",
+ "cairo-lang-syntax 2.0.2",
+ "cairo-lang-utils 2.0.2",
  "convert_case",
  "genco",
  "indoc 2.0.1",
@@ -1850,12 +1850,12 @@ dependencies = [
 
 [[package]]
 name = "cairo-lang-syntax"
-version = "2.0.0-rc6"
-source = "git+https://github.com/starkware-libs/cairo?tag=v2.0.0-rc6#54bd0e668e92c6ae504bfa0f680e22b4c29be27d"
+version = "2.0.2"
+source = "git+https://github.com/starkware-libs/cairo?tag=v2.0.2#79b34bf9dabfb1a81937a79f155857f0592cccc0"
 dependencies = [
- "cairo-lang-debug 2.0.0-rc6",
- "cairo-lang-filesystem 2.0.0-rc6",
- "cairo-lang-utils 2.0.0-rc6",
+ "cairo-lang-debug 2.0.2",
+ "cairo-lang-filesystem 2.0.2",
+ "cairo-lang-utils 2.0.2",
  "num-bigint 0.4.3",
  "num-traits 0.2.15",
  "salsa",
@@ -1888,8 +1888,8 @@ dependencies = [
 
 [[package]]
 name = "cairo-lang-syntax-codegen"
-version = "2.0.0-rc6"
-source = "git+https://github.com/starkware-libs/cairo?tag=v2.0.0-rc6#54bd0e668e92c6ae504bfa0f680e22b4c29be27d"
+version = "2.0.2"
+source = "git+https://github.com/starkware-libs/cairo?tag=v2.0.2#79b34bf9dabfb1a81937a79f155857f0592cccc0"
 dependencies = [
  "genco",
  "xshell",
@@ -1929,8 +1929,8 @@ dependencies = [
 
 [[package]]
 name = "cairo-lang-utils"
-version = "2.0.0-rc6"
-source = "git+https://github.com/starkware-libs/cairo?tag=v2.0.0-rc6#54bd0e668e92c6ae504bfa0f680e22b4c29be27d"
+version = "2.0.2"
+source = "git+https://github.com/starkware-libs/cairo?tag=v2.0.2#79b34bf9dabfb1a81937a79f155857f0592cccc0"
 dependencies = [
  "indexmap",
  "itertools",
@@ -5897,7 +5897,7 @@ checksum = "ecba01bf2678719532c5e3059e0b5f0811273d94b397088b82e3bd0a78c78fdd"
 
 [[package]]
 name = "pathfinder"
-version = "0.6.5"
+version = "0.6.6"
 dependencies = [
  "anyhow",
  "assert_matches",
@@ -5906,7 +5906,7 @@ dependencies = [
  "bytes",
  "cairo-lang-starknet 1.0.0-alpha.6",
  "cairo-lang-starknet 1.0.0-rc0",
- "cairo-lang-starknet 2.0.0-rc6",
+ "cairo-lang-starknet 2.0.2",
  "clap",
  "console-subscriber",
  "const-decoder",
```

### crates/pathfinder/Cargo.toml
```diff
@@ -21,7 +21,7 @@ async-trait = "0.1.59"
 bitvec = "0.20.4"
 casm-compiler-v1_0_0-alpha6 = { package = "cairo-lang-starknet", git = "https://github.com/starkware-libs/cairo", tag = "v1.0.0-alpha.6" }
 casm-compiler-v1_0_0-rc0 = { package = "cairo-lang-starknet", git = "https://github.com/starkware-libs/cairo", tag = "v1.0.0-rc0" }
-casm-compiler-v2_0_0-rc6 = { package = "cairo-lang-starknet", git = "https://github.com/starkware-libs/cairo", tag = "v2.0.0-rc6" }
+casm-compiler-v2 = { package = "cairo-lang-starknet", git = "https://github.com/starkware-libs/cairo", tag = "v2.0.2" }
 clap = { workspace = true, features = ["derive", "env", "wrap_help"] }
 console-subscriber = { version = "0.1.8", optional = true }
 futures = { version = "0.3", default-features = false, features = ["std"] }
```

### crates/pathfinder/src/sierra.rs
```diff
@@ -24,7 +24,7 @@ pub fn compile_to_casm(
         .parse_as_semver()
         .context("Deciding on compiler version")?
     {
-        Some(v) if v >= V_0_11_2 => v2_0_0_rc6::compile(definition),
+        Some(v) if v >= V_0_11_2 => v2::compile(definition),
         Some(v) if v >= V_0_11_1 => v1_0_0_rc0::compile(definition),
         _ => v1_0_0_alpha6::compile(definition),
     }
@@ -123,13 +123,11 @@ mod v1_0_0_rc0 {
 }
 
 // This compiler is backwards compatible with v1.1.
-mod v2_0_0_rc6 {
+mod v2 {
     use anyhow::Context;
-    use casm_compiler_v2_0_0_rc6::allowed_libfuncs::{
-        validate_compatible_sierra_version, ListSelector,
-    };
-    use casm_compiler_v2_0_0_rc6::casm_contract_class::CasmContractClass;
-    use casm_compiler_v2_0_0_rc6::contract_class::ContractClass;
+    use casm_compiler_v2::allowed_libfuncs::{validate_compatible_sierra_version, ListSelector};
+    use casm_compiler_v2::casm_contract_class::CasmContractClass;
+    use casm_compiler_v2::contract_class::ContractClass;
 
     use crate::sierra::FeederGatewayContractClass;
 
@@ -155,7 +153,7 @@ mod v2_0_0_rc6 {
         validate_compatible_sierra_version(
             &sierra_class,
             ListSelector::ListName(
-                casm_compiler_v2_0_0_rc6::allowed_libfuncs::BUILTIN_ALL_LIBFUNCS_LIST.to_string(),
+                casm_compiler_v2::allowed_libfuncs::BUILTIN_ALL_LIBFUNCS_LIST.to_string(),
             ),
         )
         .context("Validating Sierra class")?;
@@ -232,16 +230,17 @@ mod tests {
 
     mod starknet_v0_11_2_onwards {
         use super::*;
-        use starknet_gateway_test_fixtures::class_definitions::CAIRO_1_1_0_RC0_SIERRA;
+        use starknet_gateway_test_fixtures::class_definitions::{
+            CAIRO_1_1_0_RC0_SIERRA, CAIRO_2_0_0_STACK_OVERFLOW,
+        };
 
         #[test]
         fn test_feeder_gateway_contract_conversion() {
             let class =
                 serde_json::from_slice::<FeederGatewayContractClass<'_>>(CAIRO_1_1_0_RC0_SIERRA)
                     .unwrap();
 
-            let _: casm_compiler_v1_0_0_rc0::contract_class::ContractClass =
-                class.try_into().unwrap();
+            let _: casm_compiler_v2::contract_class::ContractClass = class.try_into().unwrap();
         }
 
         #[test]
@@ -251,7 +250,7 @@ mod tests {
 
         #[tokio::test]
         async fn regression_stack_overflow() {
-            // This class caused a stack-overflow in compatible compilers <= v2.0.1
+            // This class caused a stack-overflow in v2 compilers <= v2.0.1
             compile_to_casm(CAIRO_2_0_0_STACK_OVERFLOW, &StarknetVersion::new(0, 12, 0)).unwrap();
         }
     }
```
