# [?] Fix nondeterministic test error (checking for the wrong error case).

## Summary
Severity: Unknown
Chain: Zcash
Component: zcash/zcash
Published: 2022-02-03
Source: https://github.com/zcash/zcash/commit/741ed524364351d25e4f2653273611c166390211
Type: security-commit

## Details
Fix nondeterministic test error (checking for the wrong error case).

## Patch
### src/wallet/gtest/test_wallet.cpp
```diff
@@ -2224,7 +2224,7 @@ TEST(WalletTests, GenerateUnifiedAddress) {
     } else {
         // the previous generation attempt succeeded, so this one should definitely fail.
         uaResult = wallet.GenerateUnifiedAddress(0, {ReceiverType::P2PKH, ReceiverType::Sapling});
-        expected = UnifiedAddressGenerationError::DiversifierSpaceExhausted;
+        expected = UnifiedAddressGenerationError::InvalidTransparentChildIndex;
         EXPECT_EQ(uaResult, expected);
     }
 
```
