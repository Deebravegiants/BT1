# [?] fix(sigmap-EDA-06): Division by zero vulnerability in payment system (#2157)

## Summary
Severity: Unknown
Chain: EigenDA
Component: Layr-Labs/eigenda
Published: 2025-10-17
Source: https://github.com/Layr-Labs/eigenda/commit/3d37ba1ed0ba9c8355e975fc37887e007353c109
Type: security-commit

## Details
fix(sigmap-EDA-06): Division by zero vulnerability in payment system (#2157)

* fix(sigmap-EDA-06): Division by zero vulnerability in payment system

Adds validation to the `SetPaymentState()` function to reject zero
values for `reservationWindow`

* test(accountant): add test for `reservationWindow cannot be 0` err

## Patch
### api/clients/v2/accountant.go
```diff
@@ -214,6 +214,8 @@ func (a *Accountant) SetPaymentState(paymentState *disperser_rpc.GetPaymentState
 		return fmt.Errorf("payment state cannot be nil")
 	} else if paymentState.GetPaymentGlobalParams() == nil {
 		return fmt.Errorf("payment global params cannot be nil")
+	} else if paymentState.GetPaymentGlobalParams().GetReservationWindow() == 0 {
+		return fmt.Errorf("reservationWindow cannot be 0")
 	}
 
 	a.minNumSymbols = paymentState.GetPaymentGlobalParams().GetMinNumSymbols()
```

### api/clients/v2/accountant_test.go
```diff
@@ -1179,6 +1179,41 @@ func TestSetPaymentState(t *testing.T) {
 				periodRecords:     []PeriodRecord{},
 			},
 		},
+		{
+			name: "error if ReservationWindow is set to 0",
+			state: &disperser_rpc.GetPaymentStateReply{
+				PaymentGlobalParams: &disperser_rpc.PaymentGlobalParams{
+					MinNumSymbols:     100,
+					PricePerSymbol:    50,
+					ReservationWindow: 0,
+				},
+				OnchainCumulativePayment: big.NewInt(1000).Bytes(),
+				CumulativePayment:        big.NewInt(500).Bytes(),
+				Reservation: &disperser_rpc.Reservation{
+					SymbolsPerSecond: 300,
+					StartTimestamp:   100,
+					EndTimestamp:     200,
+					QuorumNumbers:    []uint32{0},
+					QuorumSplits:     []uint32{100},
+				},
+				PeriodRecords: []*disperser_rpc.PeriodRecord{
+					{
+						Index: 1,
+						Usage: 150,
+					},
+					{
+						Index: 0,
+						Usage: 0,
+					},
+					{
+						Index: 0,
+						Usage: 0,
+					},
+				},
+			},
+			expectError:  true,
+			errorMessage: "reservationWindow cannot be 0",
+		},
 	}
 
 	for _, tt := range tests {
```
