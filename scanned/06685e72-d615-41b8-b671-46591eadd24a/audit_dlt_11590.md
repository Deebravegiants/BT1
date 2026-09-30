# [?] fix#42 uint64 overflow

## Summary
Severity: Unknown
Chain: Neutron
Component: neutron-org/neutron
Published: 2025-03-14
Source: https://github.com/neutron-org/neutron/commit/693034ef0fac2cb633d94771ee543f5eb867571d
Type: security-commit

## Details
fix#42 uint64 overflow

## Patch
### x/revenue/types/payment_schedule.go
```diff
@@ -66,7 +66,7 @@ func (s *MonthlyPaymentSchedule) IntoPaymentSchedule() *PaymentSchedule {
 // PeriodEnded checks whether the end of the current payment period has come. The current period
 // ends when there has been at least BlocksPerPeriod since CurrentPeriodStartBlock.
 func (s *BlockBasedPaymentSchedule) PeriodEnded(ctx sdktypes.Context) bool {
-	return uint64(ctx.BlockHeight()) >= s.CurrentPeriodStartBlock+s.BlocksPerPeriod //nolint:gosec
+	return s.TotalBlocksInPeriod(ctx) >= s.BlocksPerPeriod //nolint:gosec
 }
 
 // TotalBlocksInPeriod returns the amount of blocks created from the beginning of the current period.
```
