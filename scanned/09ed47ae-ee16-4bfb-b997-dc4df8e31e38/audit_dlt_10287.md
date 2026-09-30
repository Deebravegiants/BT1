# [?] Fix stake underflows

## Summary
Severity: Unknown
Chain: Radix
Component: radixdlt/babylon-node
Published: 2021-07-27
Source: https://github.com/radixdlt/babylon-node/commit/1e55cd3fc5a628860d8d177153bd84730d60e3f6
Type: security-commit

## Details
Fix stake underflows

## Patch
### radixdlt-core/radixdlt/src/main/java/com/radixdlt/api/service/ValidatorArchiveInfoService.java
```diff
@@ -129,8 +129,13 @@ public ValidatorInfoDetails getNextEpochValidator(ECPublicKey k) {
 		var totalPreparedUnstakes = preparedUnstakes.values().stream().reduce(UInt256::add).orElse(UInt256.ZERO);
 		var totalStake = curData.getTotalStake().add(totalPreparedStakes).subtract(totalPreparedUnstakes);
 		var ownerStake = individualStakes.getOrDefault(owner, UInt256.ZERO)
-			.add(preparedStakes.getOrDefault(owner, UInt384.ZERO).getLow())
-			.subtract(preparedUnstakes.getOrDefault(owner, UInt256.ZERO));
+			.add(preparedStakes.getOrDefault(owner, UInt384.ZERO).getLow());
+		var ownerPreparedUnstake = preparedUnstakes.getOrDefault(owner, UInt256.ZERO);
+		if (ownerPreparedUnstake.compareTo(ownerStake) > 0) {
+			ownerStake = UInt256.ZERO;
+		} else {
+			ownerStake = ownerStake.subtract(ownerPreparedUnstake);
+		}
 		var allowsDelegation = validatorInfoService.getAllowDelegationFlag(k).allowsDelegation();
 		var isRegistered = validatorInfoService.getNextEpochRegisteredFlag(k).isRegistered();
 		var percentage = validatorInfoService.getNextValidatorFee(k).getRakePercentage();
```
