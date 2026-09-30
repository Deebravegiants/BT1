# [?] fix uint64 overflow

## Summary
Severity: Unknown
Chain: Neutron
Component: neutron-org/neutron
Published: 2025-03-21
Source: https://github.com/neutron-org/neutron/commit/23ef7421b8999a19552e3cd6295f9667525d435d
Type: security-commit

## Details
fix uint64 overflow

## Patch
### x/revenue/types/payment_schedule.go
```diff
@@ -115,7 +115,7 @@ func (s *BlockBasedPaymentSchedule) PeriodEnded(ctx sdktypes.Context) bool {
 // schedule.
 func (s *BlockBasedPaymentSchedule) EffectivePeriodProgress(ctx sdktypes.Context) math.LegacyDec {
 	switch {
-	case uint64(ctx.BlockHeight()) >= s.CurrentPeriodStartBlock+s.BlocksPerPeriod: //nolint:gosec
+	case s.PeriodEnded(ctx):
 		return math.LegacyOneDec()
 	case uint64(ctx.BlockHeight()) <= s.CurrentPeriodStartBlock: //nolint:gosec
 		return math.LegacyZeroDec()
```
