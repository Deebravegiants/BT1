# [?] routing: fix nil pointer dereference in `exitWithErr`

## Summary
Severity: Unknown
Chain: Bitcoin/Lightning
Component: lightningnetwork/lnd
Published: 2024-11-07
Source: https://github.com/lightningnetwork/lnd/commit/39584be7e1181de34e5ecdb29ea320bc50acbb10
Type: security-commit

## Details
routing: fix nil pointer dereference in `exitWithErr`

In a rare case when the critical log is triggered when using postgres as
db backend, the `payment` could be nil cause the server is shutting
down, causing the payment fetching to return an error. We now cache its
state before fetching it from the db.

## Patch
### routing/payment_lifecycle.go
```diff
@@ -189,10 +189,21 @@ func (p *paymentLifecycle) resumePayment(ctx context.Context) ([32]byte,
 		p.resultCollector(&a)
 	}
 
+	// Get the payment status.
+	status := payment.GetStatus()
+
 	// exitWithErr is a helper closure that logs and returns an error.
 	exitWithErr := func(err error) ([32]byte, *route.Route, error) {
-		log.Errorf("Payment %v with status=%v failed: %v",
-			p.identifier, payment.GetStatus(), err)
+		// Log an error with the latest payment status.
+		//
+		// NOTE: this `status` variable is reassigned in the loop
+		// below. We could also call `payment.GetStatus` here, but in a
+		// rare case when the critical log is triggered when using
+		// postgres as db backend, the `payment` could be nil, causing
+		// the payment fetching to return an error.
+		log.Errorf("Payment %v with status=%v failed: %v", p.identifier,
+			status, err)
+
 		return [32]byte{}, nil, err
 	}
 
@@ -213,10 +224,10 @@ lifecycle:
 		ps := payment.GetState()
 		remainingFees := p.calcFeeBudget(ps.FeesPaid)
 
+		status = payment.GetStatus()
 		log.Debugf("Payment %v: status=%v, active_shards=%v, "+
-			"rem_value=%v, fee_limit=%v", p.identifier,
-			payment.GetStatus(), ps.NumAttemptsInFlight,
-			ps.RemainingAmt, remainingFees)
+			"rem_value=%v, fee_limit=%v", p.identifier, status,
+			ps.NumAttemptsInFlight, ps.RemainingAmt, remainingFees)
 
 		// We now proceed our lifecycle with the following tasks in
 		// order,
```
