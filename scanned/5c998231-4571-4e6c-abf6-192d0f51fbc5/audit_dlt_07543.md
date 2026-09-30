# [?] Prevent possible from_multiplier () function overflow (#2265)

## Summary
Severity: Unknown
Chain: Nano
Component: nanocurrency/nano-node
Published: 2019-09-03
Source: https://github.com/nanocurrency/nano-node/commit/658855f6b4dbb40d961c88db4b7b516a8cf638ad
Type: security-commit

## Details
Prevent possible from_multiplier () function overflow (#2265)

* Prevent possible from_multiplier () function overflow

* Remove not required asserts

* Add more comments & test with 0 difficulty

* Update zero base difficulty test

* Formatting

## Patch
### nano/core_test/difficulty.cpp
```diff
@@ -26,6 +26,24 @@ TEST (difficulty, multipliers)
 		ASSERT_EQ (difficulty, nano::difficulty::from_multiplier (expected_multiplier, base));
 	}
 
+	{
+		uint64_t base = std::numeric_limits<std::uint64_t>::max ();
+		uint64_t difficulty = 0xffffffffffffff00;
+		double expected_multiplier = 0.00390625;
+
+		ASSERT_NEAR (expected_multiplier, nano::difficulty::to_multiplier (difficulty, base), 1e-10);
+		ASSERT_EQ (difficulty, nano::difficulty::from_multiplier (expected_multiplier, base));
+	}
+
+	{
+		uint64_t base = 0x8000000000000000;
+		uint64_t difficulty = 0xf000000000000000;
+		double expected_multiplier = 8.0;
+
+		ASSERT_NEAR (expected_multiplier, nano::difficulty::to_multiplier (difficulty, base), 1e-10);
+		ASSERT_EQ (difficulty, nano::difficulty::from_multiplier (expected_multiplier, base));
+	}
+
 	{
 #ifndef NDEBUG
 		// Causes valgrind to be noisy
@@ -46,3 +64,44 @@ TEST (difficulty, network_constants)
 {
 	ASSERT_NEAR (16., nano::difficulty::to_multiplier (nano::network_constants::publish_full_threshold, nano::network_constants::publish_beta_threshold), 1e-10);
 }
+
+TEST (difficulty, overflow)
+{
+	// Overflow max (attempt to overflow & receive lower difficulty)
+	{
+		uint64_t base = std::numeric_limits<std::uint64_t>::max (); // Max possible difficulty
+		uint64_t difficulty = std::numeric_limits<std::uint64_t>::max ();
+		double multiplier = 1.001; // Try to increase difficulty above max
+
+		ASSERT_EQ (difficulty, nano::difficulty::from_multiplier (multiplier, base));
+	}
+
+	// Overflow min (attempt to overflow & receive higher difficulty)
+	{
+		uint64_t base = 1; // Min possible difficulty before 0
+		uint64_t difficulty = 0;
+		double multiplier = 0.999; // Decrease difficulty
+
+		ASSERT_EQ (difficulty, nano::difficulty::from_multiplier (multiplier, base));
+	}
+}
+
+TEST (difficulty, zero)
+{
+	// Tests with base difficulty 0 should return 0 with any multiplier
+	{
+		uint64_t base = 0; // Min possible difficulty
+		uint64_t difficulty = 0;
+		double multiplier = 0.000000001; // Decrease difficulty
+
+		ASSERT_EQ (difficulty, nano::difficulty::from_multiplier (multiplier, base));
+	}
+
+	{
+		uint64_t base = 0; // Min possible difficulty
+		uint64_t difficulty = 0;
+		double multiplier = 1000000000.0; // Increase difficulty
+
+		ASSERT_EQ (difficulty, nano::difficulty::from_multiplier (multiplier, base));
+	}
+}
```

### nano/lib/numbers.cpp
```diff
@@ -823,7 +823,8 @@ std::string nano::to_string (double const value_a, int const precision_a)
 uint64_t nano::difficulty::from_multiplier (double const multiplier_a, uint64_t const base_difficulty_a)
 {
 	assert (multiplier_a > 0.);
-	return (-static_cast<uint64_t> ((-base_difficulty_a) / multiplier_a));
+	uint64_t reverse_difficulty (static_cast<uint64_t> ((-base_difficulty_a) / multiplier_a));
+	return (reverse_difficulty != 0 || base_difficulty_a == 0 || multiplier_a < 1. ? -reverse_difficulty : std::numeric_limits<std::uint64_t>::max ());
 }
 
 double nano::difficulty::to_multiplier (uint64_t const difficulty_a, uint64_t const base_difficulty_a)
```
