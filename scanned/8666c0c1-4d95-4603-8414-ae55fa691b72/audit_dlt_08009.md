# [?] fix: 26641: Detect overflow when validating total HBAR supply (#26642)

## Summary
Severity: Unknown
Chain: Hedera
Component: hiero-ledger/hiero-consensus-node
Published: 2026-07-31
Source: https://github.com/hiero-ledger/hiero-consensus-node/commit/1fd8c45dd96868973c830e5820d3367b63a7618c
Type: security-commit

## Details
fix: 26641: Detect overflow when validating total HBAR supply (#26642)

Signed-off-by: Nikita Lebedev <nikita.lebedev@limechain.tech>

## Patch
### hedera-state-validator/src/main/java/com/hedera/statevalidation/validator/AccountAndSupplyValidator.java
```diff
@@ -110,7 +110,7 @@ public void processLeafBytes(long dataLocation, @NonNull final VirtualLeafBytes<
                     invalidAccountBalanceCount.incrementAndGet();
                     log.error("Invalid balance for account {}", account.accountId());
                 }
-                totalBalance.addAndGet(tinybarBalance);
+                totalBalance.accumulateAndGet(tinybarBalance, Math::addExact);
                 accountsCreated.incrementAndGet();
             } catch (final ParseException e) {
                 throw new RuntimeException("Failed to parse a key", e);
```
