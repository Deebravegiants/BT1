# [?] (fix): detect ecrecover overflow (#2080)

## Summary
Severity: Unknown
Chain: Linea
Component: LFDT-Lineth/lineth-monorepo
Published: 2026-01-20
Source: https://github.com/LFDT-Lineth/lineth-monorepo/commit/b2768fa17abc10d219f608fc6777ae8e3fa9b991
Type: security-commit

## Details
(fix): detect ecrecover overflow (#2080)

## Patch
### prover/zkevm/prover/ecdsa/antichamber.go
```diff
@@ -187,6 +187,14 @@ func (ac *antichamber) assignAntichamber(run *wizard.ProverRuntime, nbEcRecInsta
 	var (
 		maxNbEcRecover = ac.Inputs.Settings.MaxNbEcRecover
 		maxNbTx        = ac.Inputs.Settings.MaxNbTx
+
+		// Calculate the Logical Limit (The "Contract")
+		// This is the maximum row space we claimed we would need in your config.
+		// The circuit is built to exactly this capacity.
+		configuredLimitRows = nbRowsPerEcRec*maxNbEcRecover + nbRowsPerTxSign*maxNbTx
+
+		// Calculate Actual Usage (The "Reality") - This is how many rows your trace actually demands.
+		actualUsageRows = nbRowsPerEcRec*nbEcRecInstances + nbRowsPerTxSign*nbTxInstances
 	)
 
 	if nbRowsPerEcRec*maxNbEcRecover+nbRowsPerTxSign*maxNbTx > ac.Size {
@@ -211,6 +219,17 @@ func (ac *antichamber) assignAntichamber(run *wizard.ProverRuntime, nbEcRecInsta
 		)
 	}
 
+	// This catches the case where the data fits in the physical buffer (ac.Size)
+	// but exceeds the logical capacity the circuit was built for.
+	if actualUsageRows > configuredLimitRows {
+		exit.OnLimitOverflow(
+			configuredLimitRows,
+			actualUsageRows,
+			fmt.Errorf("ECDSA antichamber row limit exceeded: trace requires %d rows (EcRec:%d, Tx:%d), but config limits to %d rows (MaxEcRec:%d, MaxTx:%d)",
+				actualUsageRows, nbEcRecInstances, nbTxInstances, configuredLimitRows, maxNbEcRecover, maxNbTx),
+		)
+	}
+
 	// allocate the columns for preparing the assignment
 	resIsActive := make([]field.Element, ac.Size)
 	resID := make([]field.Element, ac.Size)
```
