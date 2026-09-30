# [?] onchaind: fix crash if we enounter a tx with no witness.

## Summary
Severity: Unknown
Chain: Bitcoin/Lightning
Component: ElementsProject/lightning
Published: 2025-03-04
Source: https://github.com/ElementsProject/lightning/commit/c92c3848750dffc478e7e1e24b5cc3c82093b558
Type: security-commit

## Details
onchaind: fix crash if we enounter a tx with no witness.

This can happen if a descendent tx has no witness and we don't tell the main daemon
in time that we're not iterested.

Fixes: https://github.com/ElementsProject/lightning/issues/8133
Changelog-Fixed: lightningd: onchaind crash when seeing unrelated txs (usually when catching up with old closes)
Signed-off-by: Rusty Russell <rusty@rustcorp.com.au>

## Patch
### onchaind/onchaind.c
```diff
@@ -774,7 +774,7 @@ static bool resolved_by_proposal(struct tracked_output *out,
 		return false;
 
 	input = which_input_spends(tx_parts, &out->outpoint);
-	if (!input)
+	if (!input || !input->witness)
 		return false;
 	if (!onchain_witness_element_matches(out->proposal->welements, input))
 		return false;
```
