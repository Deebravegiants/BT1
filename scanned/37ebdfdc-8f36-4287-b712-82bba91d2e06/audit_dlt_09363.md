# [?] fix: avoid oob access in RAM / ROM and enable soft-fail (#22301)

## Summary
Severity: Unknown
Chain: Aztec
Component: AztecProtocol/aztec-packages
Published: 2026-04-03
Source: https://github.com/AztecProtocol/aztec-packages/commit/ea01329530ed07d32e65164ee50158cd282ee201
Type: security-commit

## Details
fix: avoid oob access in RAM / ROM and enable soft-fail (#22301)

Fixes minor OOB issue with RAM / ROM: circuit should not crash due to
OOB.

## Patch
### barretenberg/cpp/src/barretenberg/stdlib/primitives/memory/ram_table.cpp
```diff
@@ -228,9 +228,9 @@ template <typename Builder> void ram_table<Builder>::write(const field_pt& index
     initialize_table();
 
     if (uint256_t(index.get_value()) >= length) {
-        // set a failure when the index is out of bounds. an error will be thrown when we try to call either
-        // `init_RAM_element` or `write_RAM_array`.
+        // set a failure when the index is out of bounds. Return early to avoid OOB vector access.
         context->failure("ram_table: RAM array access out of bounds");
+        return;
     }
 
     field_pt index_wire = index;
```

### barretenberg/cpp/src/barretenberg/stdlib/primitives/memory/ram_table.test.cpp
```diff
@@ -169,3 +169,28 @@ TYPED_TEST(RamTableTests, RamTableReadWriteConsistency)
     bool verified = CircuitChecker::check(builder);
     EXPECT_EQ(verified, true);
 }
+
+/**
+ * @brief OOB write soft-fails correctly without crashing.
+ */
+TEST(RamTable, OobWriteDoesNotCrashRegression)
+{
+    using Builder = UltraCircuitBuilder;
+    using field_ct = stdlib::field_t<Builder>;
+    using ram_table_ct = stdlib::ram_table<Builder>;
+
+    Builder builder;
+
+    const size_t table_size = 3;
+    std::vector<field_ct> init_values(table_size, field_ct(0));
+    ram_table_ct table(&builder, init_values);
+
+    for (size_t i = 0; i < table_size; ++i) {
+        table.write(i, field_ct(bb::fr(i)));
+    }
+
+    // OOB write — should soft-fail, not crash
+    table.write(field_ct(100000000), field_ct(bb::fr(42)));
+
+    EXPECT_TRUE(builder.failed());
+}
```

### barretenberg/cpp/src/barretenberg/stdlib/primitives/memory/rom_table.cpp
```diff
@@ -153,6 +153,7 @@ template <typename Builder> field_t<Builder> rom_table<Builder>::operator[](cons
     if (index >= length) {
         BB_ASSERT(context != nullptr);
         context->failure("rom_table: ROM array access out of bounds");
+        return raw_entries[0];
     }
 
     return raw_entries[index];
```

### barretenberg/cpp/src/barretenberg/stdlib/primitives/memory/rom_table.test.cpp
```diff
@@ -143,3 +143,27 @@ TYPED_TEST(RomTableTests, RomCopy)
     bool verified = CircuitChecker::check(builder);
     EXPECT_EQ(verified, true);
 }
+
+/**
+ * @brief OOB constant-index access soft-fails correctly without crashing.
+ */
+TEST(RomTable, OobConstantIndexDoesNotCrashRegression)
+{
+    using Builder = UltraCircuitBuilder;
+    using field_ct = stdlib::field_t<Builder>;
+    using witness_ct = stdlib::witness_t<Builder>;
+    using rom_table_ct = stdlib::rom_table<Builder>;
+
+    Builder builder;
+
+    std::vector<field_ct> table_values;
+    table_values.emplace_back(witness_ct(&builder, bb::fr(1)));
+    table_values.emplace_back(witness_ct(&builder, bb::fr(2)));
+    table_values.emplace_back(witness_ct(&builder, bb::fr(3)));
+    rom_table_ct table(table_values);
+
+    // OOB constant index — should soft-fail, not crash
+    table[static_cast<size_t>(100000000)];
+
+    EXPECT_TRUE(builder.failed());
+}
```

### barretenberg/cpp/src/barretenberg/stdlib/primitives/memory/twin_rom_table.cpp
```diff
@@ -132,6 +132,7 @@ std::array<field_t<Builder>, 2> twin_rom_table<Builder>::operator[](const size_t
     if (index >= length) {
         BB_ASSERT(context != nullptr);
         context->failure("twin_rom_table: ROM array access out of bounds");
+        return raw_entries[0];
     }
 
     return raw_entries[index];
```

### barretenberg/cpp/src/barretenberg/stdlib/primitives/memory/twin_rom_table.test.cpp
```diff
@@ -136,3 +136,27 @@ TYPED_TEST(TwinRomTableTests, ReadWriteConsistency)
     bool verified = CircuitChecker::check(builder);
     EXPECT_EQ(verified, true);
 }
+
+/**
+ * @brief OOB constant-index access soft-fails correctly without crashing.
+ */
+TEST(TwinRomTable, OobConstantIndexDoesNotCrashRegression)
+{
+    using Builder = UltraCircuitBuilder;
+    using field_ct = stdlib::field_t<Builder>;
+    using witness_ct = stdlib::witness_t<Builder>;
+    using twin_rom_table_ct = stdlib::twin_rom_table<Builder>;
+    using field_pair_ct = std::array<field_ct, 2>;
+
+    Builder builder;
+
+    std::vector<field_pair_ct> table_values;
+    table_values.emplace_back(field_pair_ct{ witness_ct(&builder, bb::fr(1)), witness_ct(&builder, bb::fr(2)) });
+    table_values.emplace_back(field_pair_ct{ witness_ct(&builder, bb::fr(3)), witness_ct(&builder, bb::fr(4)) });
+    twin_rom_table_ct table(table_values);
+
+    // OOB constant index — should soft-fail, not crash
+    table[static_cast<size_t>(100000000)];
+
+    EXPECT_TRUE(builder.failed());
+}
```
