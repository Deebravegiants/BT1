# [?] fix(x/slashing): consensus failure after cons key rotation (#19038)

## Summary
Severity: Unknown
Chain: Cosmos
Component: cosmos/cosmos-sdk
Published: 2024-01-12
Source: https://github.com/cosmos/cosmos-sdk/commit/eaf92c225cfa2420946ff738cdcf05cf8b402040
Type: security-commit

## Details
fix(x/slashing): consensus failure after cons key rotation (#19038)

## Patch
### x/slashing/keeper/infractions.go
```diff
@@ -32,15 +32,23 @@ func (k Keeper) HandleValidatorSignatureWithParams(ctx context.Context, params t
 	consAddr := sdk.ConsAddress(addr)
 
 	// don't update missed blocks when validator's jailed
-	isJailed, err := k.sk.IsValidatorJailed(ctx, consAddr)
+	val, err := k.sk.ValidatorByConsAddr(ctx, consAddr)
 	if err != nil {
 		return err
 	}
 
-	if isJailed {
+	if val.IsJailed() {
 		return nil
 	}
 
+	// read the cons address again because validator may've rotated it's key
+	valConsAddr, err := val.GetConsAddr()
+	if err != nil {
+		return err
+	}
+
+	consAddr = sdk.ConsAddress(valConsAddr)
+
 	// fetch signing info
 	signInfo, err := k.ValidatorSigningInfo.Get(ctx, consAddr)
 	if err != nil {
```

### x/slashing/keeper/signing_info.go
```diff
@@ -252,6 +252,12 @@ func (k Keeper) performConsensusPubKeyUpdate(ctx context.Context, oldPubKey, new
 		return types.ErrInvalidConsPubKey.Wrap("failed to get signing info for old public key")
 	}
 
+	consAddr, err := k.sk.ConsensusAddressCodec().BytesToString(newPubKey.Address())
+	if err != nil {
+		return err
+	}
+
+	signingInfo.Address = consAddr
 	if err := k.ValidatorSigningInfo.Set(ctx, sdk.ConsAddress(newPubKey.Address()), signingInfo); err != nil {
 		return err
 	}
```

### x/slashing/keeper/signing_info_test.go
```diff
@@ -124,7 +124,7 @@ func (s *KeeperTestSuite) TestPerformConsensusPubKeyUpdate() {
 	newConsAddr := sdk.ConsAddress(pks[1].Address())
 
 	newInfo := slashingtypes.NewValidatorSigningInfo(
-		oldConsAddr.String(),
+		newConsAddr.String(),
 		int64(4),
 		int64(3),
 		time.Unix(2, 0).UTC(),
```
