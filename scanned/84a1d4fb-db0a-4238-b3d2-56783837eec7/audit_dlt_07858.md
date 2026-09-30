# [?] Fix slot calculation underflow (#2863)

## Summary
Severity: Unknown
Chain: Ethereum
Component: Consensys-Incorporated/teku
Published: 2020-09-28
Source: https://github.com/Consensys-Incorporated/teku/commit/7ae0a7579212034103936bfdb0ae2ac22275120a
Type: security-commit

## Details
Fix slot calculation underflow (#2863)

## Patch
### ethereum/core/src/main/java/tech/pegasys/teku/core/ForkChoiceUtil.java
```diff
@@ -59,6 +59,9 @@ public static UInt64 get_slots_since_genesis(ReadOnlyStore store, boolean useUni
   }
 
   public static UInt64 getCurrentSlot(UInt64 currentTime, UInt64 genesisTime) {
+    if (currentTime.isLessThan(genesisTime)) {
+      return UInt64.ZERO;
+    }
     return currentTime.minus(genesisTime).dividedBy(SECONDS_PER_SLOT);
   }
 
```

### ethereum/core/src/test/java/tech/pegasys/teku/core/ForkChoiceUtilTest.java
```diff
@@ -138,6 +138,12 @@ public void getCurrentSlot_shouldGetNonZeroPastGenesis() {
     assertThat(ForkChoiceUtil.getCurrentSlot(SLOT_50, GENESIS_TIME)).isEqualTo(UInt64.valueOf(50L));
   }
 
+  @Test
+  public void getCurrentSlot_shouldGetZeroPriorToGenesis() {
+    assertThat(ForkChoiceUtil.getCurrentSlot(GENESIS_TIME.minus(1), GENESIS_TIME))
+        .isEqualTo(UInt64.ZERO);
+  }
+
   @Test
   public void getSlotStartTime_shouldGetGenesisTimeForBlockZero() {
     assertThat(ForkChoiceUtil.getSlotStartTime(UInt64.ZERO, GENESIS_TIME)).isEqualTo(GENESIS_TIME);
```
