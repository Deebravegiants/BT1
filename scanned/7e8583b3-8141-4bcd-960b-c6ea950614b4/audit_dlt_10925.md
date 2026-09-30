# [?] Check the upper limit of difficulty to prevent data overflow

## Summary
Severity: Unknown
Chain: Zilliqa
Component: Zilliqa/zq1
Published: 2019-03-20
Source: https://github.com/Zilliqa/zq1/commit/4766f89ee56efee722a1f07a081131e264fe9b95
Type: security-commit

## Details
Check the upper limit of difficulty to prevent data overflow

## Patch
### src/libDirectoryService/DirectoryService.cpp
```diff
@@ -1053,6 +1053,12 @@ uint8_t DirectoryService::CalculateNewDifficultyCore(uint8_t currentDifficulty,
     }
   }
 
+  // Already reach the highest difficulty, cannot increase any more
+  if (adjustment > 0 &&
+      currentDifficulty >= std::numeric_limits<uint8_t>::max()) {
+    return currentDifficulty;
+  }
+
   // Restrict the adjustment step, prevent the difficulty jump up/down
   // dramatically.
   if (adjustment > MAX_ADJUST_STEP) {
```

### tests/POW/test_POW.cpp
```diff
@@ -883,6 +883,20 @@ BOOST_AUTO_TEST_CASE(devided_difficulty_adjustment_for_ds_large) {
   BOOST_REQUIRE(newDifficulty == 69);
 }
 
+BOOST_AUTO_TEST_CASE(test_highest_difficulty) {
+  std::cout << "Start test highest difficulty" << std::endl;
+  uint8_t currentDifficulty = 255;
+  uint8_t minDifficulty = 5;
+  int64_t powSubmissions = 110;
+  int64_t expectedNodes = 100;
+  uint32_t adjustThreshold = 9;
+
+  int newDifficulty = DirectoryService::CalculateNewDifficultyCore(
+      currentDifficulty, minDifficulty, powSubmissions, expectedNodes,
+      adjustThreshold);
+  BOOST_REQUIRE(newDifficulty == 255);
+}
+
 BOOST_AUTO_TEST_CASE(devided_boundary) {
   std::cout << "Start test devided_boundary" << std::endl;
 
```
