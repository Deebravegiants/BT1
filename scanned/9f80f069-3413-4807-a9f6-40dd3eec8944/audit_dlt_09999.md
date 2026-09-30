# [?] fix for to_uint256_t array overflow and some unit tests

## Summary
Severity: Unknown
Chain: Monad
Component: category-labs/monad
Published: 2024-08-14
Source: https://github.com/category-labs/monad/commit/af97b98ae1326911add526c3e627d1180782d6b8
Type: security-commit

## Details
fix for to_uint256_t array overflow and some unit tests

## Patch
### libs/vm/src/compiler/include/compiler/ir/bytecode.h
```diff
@@ -20,6 +20,8 @@ namespace monad::compiler
         uint256_t token_data; // only used by push
     };
 
+    bool operator==(Token const &a, Token const &b);
+
     class BytecodeIR
     {
     public:
```

### libs/vm/src/compiler/include/compiler/ir/instruction.h
```diff
@@ -32,6 +32,8 @@ namespace monad::compiler
                                    // INVALID_BLOCK_ID
     };
 
+    bool operator==(Block const &a, Block const &b);
+
     class InstructionIR
     {
     public:
```

### libs/vm/src/compiler/ir/bytecode.cpp
```diff
@@ -1,3 +1,4 @@
+#include <algorithm>
 #include <compiler/ir/bytecode.h>
 
 #include <intx/intx.hpp>
@@ -11,7 +12,8 @@
 
 namespace
 {
-    uint256_t to_uint256_t(std::size_t const n, uint8_t const *src)
+    uint256_t to_uint256_t(
+        std::size_t const n, std::size_t const remaining, uint8_t const *src)
     {
         assert(n <= 32);
 
@@ -21,7 +23,7 @@ namespace
 
         uint8_t dst[32] = {};
 
-        std::memcpy(dst, src, n);
+        std::memcpy(&dst[32 - n], src, std::min(n, remaining));
 
         return intx::be::load<uint256_t>(dst);
     }
@@ -36,10 +38,26 @@ namespace monad::compiler
         while (curr_offset < byte_code.size()) {
             uint8_t const opcode = byte_code[curr_offset];
             std::size_t const n = opcode_info_table[opcode].num_args;
+            byte_offset const opcode_offset = curr_offset;
+
+            curr_offset++;
+
             tokens.emplace_back(
-                curr_offset, opcode, to_uint256_t(n, &byte_code[curr_offset]));
-            curr_offset += 1 + n;
+                opcode_offset,
+                opcode,
+                to_uint256_t(
+                    n,
+                    byte_code.size() - curr_offset,
+                    &byte_code[curr_offset]));
+
+            curr_offset += n;
         }
     }
 
+    bool operator==(Token const &a, Token const &b)
+    {
+        return a.token_offset == b.token_offset &&
+               a.token_opcode == b.token_opcode && a.token_data == b.token_data;
+    }
+
 }
```

### libs/vm/src/compiler/ir/instruction.cpp
```diff
@@ -7,6 +7,12 @@
 namespace monad::compiler
 {
 
+    bool operator==(Block const &a, Block const &b)
+    {
+        return a.instrs == b.instrs && a.terminator == b.terminator &&
+               a.fallthrough_dest == b.fallthrough_dest;
+    }
+
     block_id InstructionIR::curr_block_id() const
     {
         return blocks.size() - 1;
```

### libs/vm/src/test/CMakeLists.txt
```diff
@@ -1,3 +1,17 @@
+add_executable(compiler-tests compiler_tests.cpp)
+
+monad_compile_options(compiler-tests)
+target_link_libraries(compiler-tests compiler GTest::gtest_main)
+target_include_directories(compiler-tests
+    PRIVATE ../compiler/include/
+    PRIVATE ../../third_party/intx/include/
+)
+
+add_test(
+    NAME "Compiler Tests"
+    COMMAND compiler-tests
+)
+
 add_executable(vm-tests vm_tests.cpp)
 
 monad_compile_options(vm-tests)
@@ -7,4 +21,4 @@ target_include_directories(vm-tests PRIVATE include/)
 add_test(
     NAME "VM Tests"
     COMMAND vm-tests
-)
\ No newline at end of file
+)
```

### libs/vm/src/test/compiler_tests.cpp
```diff
@@ -0,0 +1,99 @@
+#include <cstdint>
+#include <gtest/gtest.h>
+#include <unordered_map>
+#include <vector>
+
+#include <compiler/ir/bytecode.h>
+#include <compiler/ir/instruction.h>
+
+using namespace monad::compiler;
+
+void tokens_eq(std::vector<uint8_t> const &in, std::vector<Token> const &expected)
+{
+    EXPECT_EQ(BytecodeIR(in).tokens, expected);
+}
+
+TEST(BytecodeTest, ToTokens)
+{
+    tokens_eq({}, {});
+    tokens_eq({STOP}, {{0, STOP, 0}});
+    tokens_eq({0xee}, {{0, 0xee, 0}});
+    tokens_eq({PUSH0}, {{0, PUSH0, 0}});
+    tokens_eq({PUSH1, 0xff}, {{0, PUSH1, 0xff}});
+    tokens_eq({PUSH2, 0xff, 0xee}, {{0, PUSH2, 0xffee}});
+    tokens_eq({PUSH1, 0xff, PUSH1, 0xee}, {{0, PUSH1, 0xff}, {2, PUSH1, 0xee}});
+    tokens_eq(
+        {STOP, PUSH2, 0xaa, 0xbb, 0xee},
+        {{0, STOP, 0}, {1, PUSH2, 0xaabb}, {4, 0xee, 0}});
+    tokens_eq({PUSH1}, {{0, PUSH1, 0x0}});
+    tokens_eq({PUSH2, 0xff}, {{0, PUSH2, 0xff00}});
+    tokens_eq({PUSH4, 0xaa, 0xbb}, {{0, PUSH4, 0xaabb0000}});
+    tokens_eq({PUSH32, 0xff}, {{0, PUSH32, (uint256_t)0xff << 248}});
+}
+
+void blocks_eq(std::vector<uint8_t> const &in,
+    std::unordered_map<byte_offset, block_id> const &expected_jumpdests,
+    std::vector<Block> const &expected_blocks
+               )
+{
+    BytecodeIR const actual_bc(in);
+    InstructionIR const actual(actual_bc);
+
+    EXPECT_EQ(actual.jumpdests, expected_jumpdests);
+    EXPECT_EQ(actual.blocks, expected_blocks);
+}
+
+
+using Terminator::JumpDest;
+using Terminator::JumpI;
+using Terminator::Jump;
+using Terminator::Return;
+using Terminator::Stop;
+using Terminator::Revert;
+using Terminator::SelfDestruct;
+
+TEST(InstructionTest, ToBlocks)
+{
+    blocks_eq({}, {}, {{{}, Stop, INVALID_BLOCK_ID}});
+    blocks_eq({STOP}, {}, {{{}, Stop, INVALID_BLOCK_ID}});
+    blocks_eq({0xEE}, {}, {
+        {{{0, 0xEE, 0}}, Stop, INVALID_BLOCK_ID}});
+    blocks_eq({PUSH1}, {}, {
+        {{{0, PUSH1, 0}}, Stop, INVALID_BLOCK_ID}});
+    blocks_eq({PUSH2,0xf}, {}, {
+        {{{0, PUSH2, 0xf00}}, Stop, INVALID_BLOCK_ID}});
+    blocks_eq({STOP,ADD}, {}, {
+        {{}, Stop, INVALID_BLOCK_ID}});
+    blocks_eq({JUMPDEST, STOP}, {{0,0}}, {
+        {{}, Stop, INVALID_BLOCK_ID}});
+    blocks_eq({ADD, REVERT}, {}, {
+        {{{0, ADD, 0}}, Revert, INVALID_BLOCK_ID}});
+    blocks_eq({ADD, ADD, RETURN}, {}, {
+        {{{0, ADD, 0},{1, ADD, 0}}, Return, INVALID_BLOCK_ID}});
+    blocks_eq({JUMPDEST, ADD, REVERT}, {{0,0}}, {
+        {{{1, ADD, 0}}, Revert, INVALID_BLOCK_ID}});
+    blocks_eq({JUMPI}, {}, {
+        {{}, JumpI, 1},
+        {{}, Stop, INVALID_BLOCK_ID}
+        });
+    blocks_eq({JUMPDEST,JUMPDEST}, {{0,0},{1,0}}, {
+        {{}, Stop, INVALID_BLOCK_ID}
+        });
+    blocks_eq({JUMPDEST,JUMPDEST,JUMPDEST}, {{0,0},{1,0},{2,0}}, {
+        {{}, Stop, INVALID_BLOCK_ID}
+        });
+    blocks_eq({JUMPDEST,ADD,JUMPDEST}, {{0,0},{2,1}}, {
+        {{{1, ADD, 0}}, JumpDest, 1},
+        {{}, Stop, INVALID_BLOCK_ID}
+        });
+    blocks_eq({ADD, ADD, JUMP, ADD, JUMPDEST, SELFDESTRUCT}, {{4,1}}, {
+        {{{0, ADD, 0},{1, ADD, 0}}, Jump, INVALID_BLOCK_ID},
+        {{}, SelfDestruct, INVALID_BLOCK_ID}
+        });
+    blocks_eq({ADD, ADD, JUMP, ADD, JUMPDEST, JUMPDEST, SELFDESTRUCT}, {{4,1},{5, 1}}, {
+        {{{0, ADD, 0},{1, ADD, 0}}, Jump, INVALID_BLOCK_ID},
+        {{}, SelfDestruct, INVALID_BLOCK_ID}
+        });
+
+}
+
```
