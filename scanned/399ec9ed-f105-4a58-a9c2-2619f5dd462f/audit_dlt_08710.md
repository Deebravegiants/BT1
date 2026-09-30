# [?] Fix L2PricingState UpdatePricingModel panic if chain owner sets insane parameters

## Summary
Severity: Unknown
Chain: Arbitrum
Component: OffchainLabs/nitro
Published: 2025-06-02
Source: https://github.com/OffchainLabs/nitro/commit/4cb87e433c0d63a54173898c6f1108de5a65611e
Type: security-commit

## Details
Fix L2PricingState UpdatePricingModel panic if chain owner sets insane parameters

## Patch
### arbos/l2pricing/model.go
```diff
@@ -50,7 +50,7 @@ func (ps *L2PricingState) UpdatePricingModel(l2BaseFee *big.Int, timePassed uint
 	baseFee := minBaseFee
 	if backlog > tolerance*speedLimit {
 		excess := arbmath.SaturatingCast[int64](backlog - tolerance*speedLimit)
-		exponentBips := arbmath.NaturalToBips(excess) / arbmath.SaturatingCast[arbmath.Bips](inertia*speedLimit)
+		exponentBips := arbmath.NaturalToBips(excess) / arbmath.SaturatingCast[arbmath.Bips](arbmath.SaturatingUMul(inertia, speedLimit))
 		baseFee = arbmath.BigMulByBips(minBaseFee, arbmath.ApproxExpBasisPoints(exponentBips, 4))
 	}
 	_ = ps.SetBaseFeeWei(baseFee)
```

### precompiles/ArbOwner.go
```diff
@@ -141,6 +141,9 @@ func (con ArbOwner) SetMinimumL2BaseFee(c ctx, evm mech, priceInWei huge) error
 
 // SetSpeedLimit sets the computational speed limit for the chain
 func (con ArbOwner) SetSpeedLimit(c ctx, evm mech, limit uint64) error {
+	if limit == 0 {
+		return errors.New("speed limit must be nonzero")
+	}
 	return c.State.L2PricingState().SetSpeedLimitPerSecond(limit)
 }
 
@@ -151,6 +154,9 @@ func (con ArbOwner) SetMaxTxGasLimit(c ctx, evm mech, limit uint64) error {
 
 // SetL2GasPricingInertia sets the L2 gas pricing inertia
 func (con ArbOwner) SetL2GasPricingInertia(c ctx, evm mech, sec uint64) error {
+	if sec == 0 {
+		return errors.New("price inertia must be nonzero")
+	}
 	return c.State.L2PricingState().SetPricingInertia(sec)
 }
 
```
