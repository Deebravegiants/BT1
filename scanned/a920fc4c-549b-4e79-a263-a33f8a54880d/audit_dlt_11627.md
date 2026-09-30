# [?] guard against panic in spot price

## Summary
Severity: Unknown
Chain: Quicksilver
Component: quicksilver-zone/quicksilver
Published: 2025-07-15
Source: https://github.com/quicksilver-zone/quicksilver/commit/a09e26ff9105118171e6bde975cc3cde0faf6b90
Type: security-commit

## Details
guard against panic in spot price

## Patch
### third-party-chains/osmosis-types/concentrated-liquidity/model/pool.go
```diff
@@ -125,6 +125,9 @@ func (p Pool) SpotPrice(ctx sdk.Context, quoteAssetDenom string, baseAssetDenom
 	if baseAssetDenom == p.Token0 {
 		return osmomath.BigDecFromDecMut(priceSquared.Dec()), nil
 	}
+	if priceSquared.IsZero() {
+		return osmomath.BigDec{}, fmt.Errorf("price squared is zero")
+	}
 	return osmomath.BigDecFromDecMut(osmomath.OneBigDec().QuoMut(priceSquared).Dec()), nil
 }
 
```
