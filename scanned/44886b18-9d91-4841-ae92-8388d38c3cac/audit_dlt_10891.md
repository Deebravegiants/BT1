# [?] api/blocks: fix panic on reverted tx

## Summary
Severity: Unknown
Chain: VeChain
Component: vechain/thor
Published: 2020-03-12
Source: https://github.com/vechain/thor/commit/2951d204981ba4d2e493b739046d5866a7db9af9
Type: security-commit

## Details
api/blocks: fix panic on reverted tx

## Patch
### api/blocks/types.go
```diff
@@ -111,12 +111,7 @@ func buildJSONBlockSummary(summary *chain.BlockSummary, isTrunk bool) *JSONBlock
 	}
 }
 
-func buildJSONClauseOutput(txID thor.Bytes32, index uint32, c *tx.Clause, o *tx.Output) (*JSONClause, *JSONOutput) {
-	jc := &JSONClause{
-		c.To(),
-		math.HexOrDecimal256(*c.Value()),
-		hexutil.Encode(c.Data()),
-	}
+func buildJSONOutput(txID thor.Bytes32, index uint32, c *tx.Clause, o *tx.Output) *JSONOutput {
 	jo := &JSONOutput{
 		ContractAddress: nil,
 		Events:          make([]*JSONEvent, 0, len(o.Events)),
@@ -140,7 +135,7 @@ func buildJSONClauseOutput(txID thor.Bytes32, index uint32, c *tx.Clause, o *tx.
 			Amount:    (*math.HexOrDecimal256)(t.Amount),
 		})
 	}
-	return jc, jo
+	return jo
 }
 
 func buildJSONEmbeddedTxs(txs tx.Transactions, receipts tx.Receipts) []*JSONEmbeddedTx {
@@ -157,10 +152,14 @@ func buildJSONEmbeddedTxs(txs tx.Transactions, receipts tx.Receipts) []*JSONEmbe
 		jos := make([]*JSONOutput, 0, len(receipt.Outputs))
 
 		for i, c := range clauses {
-			o := receipt.Outputs[i]
-			jc, jo := buildJSONClauseOutput(tx.ID(), uint32(i), c, o)
-			jcs = append(jcs, jc)
-			jos = append(jos, jo)
+			jcs = append(jcs, &JSONClause{
+				c.To(),
+				math.HexOrDecimal256(*c.Value()),
+				hexutil.Encode(c.Data()),
+			})
+			if !receipt.Reverted {
+				jos = append(jos, buildJSONOutput(tx.ID(), uint32(i), c, receipt.Outputs[i]))
+			}
 		}
 
 		jTxs = append(jTxs, &JSONEmbeddedTx{
```
