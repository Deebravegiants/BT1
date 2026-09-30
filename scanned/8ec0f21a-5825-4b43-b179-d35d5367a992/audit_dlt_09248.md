# [?] Fix stack overflow issue when using soljson compiler

## Summary
Severity: Unknown
Chain: Solidity
Component: argotorg/solidity
Published: 2025-02-19
Source: https://github.com/argotorg/solidity/commit/3532328324cc479d17b4492de645597a3b5282c1
Type: security-commit

## Details
Fix stack overflow issue when using soljson compiler

## Patch
### cmake/EthCompilerSettings.cmake
```diff
@@ -170,6 +170,10 @@ if (("${CMAKE_CXX_COMPILER_ID}" MATCHES "GNU") OR ("${CMAKE_CXX_COMPILER_ID}" MA
 			set(CMAKE_EXE_LINKER_FLAGS "${CMAKE_EXE_LINKER_FLAGS} -s ALLOW_TABLE_GROWTH=1")
 			# Disable warnings about not being pure asm.js due to memory growth.
 			set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -Wno-almost-asm")
+			# Increase stack size from 5MB to 16MB to prevent stack overflow issues.
+			set(CMAKE_EXE_LINKER_FLAGS "${CMAKE_EXE_LINKER_FLAGS} -s TOTAL_STACK=16mb")
+			# Increase memory size from 16MB to 32MB since the stack size is now 16MB.
+			set(CMAKE_EXE_LINKER_FLAGS "${CMAKE_EXE_LINKER_FLAGS} -s INITIAL_MEMORY=32mb")
 		endif()
 	endif()
 
```
