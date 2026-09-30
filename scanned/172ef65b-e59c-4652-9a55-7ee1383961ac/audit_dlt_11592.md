# [?] Audit fix: ensure we cannot overflow/wrap uint with large fees

## Summary
Severity: Unknown
Chain: Neutron
Component: neutron-org/neutron
Published: 2024-05-27
Source: https://github.com/neutron-org/neutron/commit/f1e5f589aa18d8eba875523be87070139cde2388
Type: security-commit

## Details
Audit fix: ensure we cannot overflow/wrap uint with large fees

## Patch
### x/dex/keeper/msg_server_test.go
```diff
@@ -1753,6 +1753,19 @@ func TestMsgDepositValidate(t *testing.T) {
 			},
 			types.ErrTickOutsideRange,
 		},
+		{
+			"invalid fee overflow",
+			types.MsgDeposit{
+				Creator:         sample.AccAddress(),
+				Receiver:        sample.AccAddress(),
+				Fees:            []uint64{559681},
+				TickIndexesAToB: []int64{0},
+				AmountsA:        []sdkmath.Int{sdkmath.OneInt()},
+				AmountsB:        []sdkmath.Int{sdkmath.OneInt()},
+				Options:         []*types.DepositOptions{{DisableAutoswap: false}},
+			},
+			types.ErrInvalidFee,
+		},
 	}
 
 	for _, tt := range tests {
@@ -1873,6 +1886,17 @@ func TestMsgWithdrawalValidate(t *testing.T) {
 			},
 			types.ErrTickOutsideRange,
 		},
+		{
+			"invalid fee overflow",
+			types.MsgWithdrawal{
+				Creator:         sample.AccAddress(),
+				Receiver:        sample.AccAddress(),
+				Fees:            []uint64{559681},
+				TickIndexesAToB: []int64{0},
+				SharesToRemove:  []sdkmath.Int{sdkmath.OneInt()},
+			},
+			types.ErrInvalidFee,
+		},
 	}
 
 	for _, tt := range tests {
```

### x/dex/types/price.go
```diff
@@ -37,6 +37,10 @@ func IsTickOutOfRange(tickIndex int64) bool {
 }
 
 func ValidateTickFee(tick int64, fee uint64) error {
+	// Ensure we do not overflow/wrap Uint
+	if fee >= MaxTickExp {
+		return ErrInvalidFee
+	}
 	// Ensure |tick| + fee <= MaxTickExp
 	// NOTE: Ugly arithmetic is to ensure that we don't overflow uint64
 	if utils.Abs(tick) > MaxTickExp-fee {
```
