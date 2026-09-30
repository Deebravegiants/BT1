# [?] askrene: fix payment crash

## Summary
Severity: Unknown
Chain: Bitcoin/Lightning
Component: ElementsProject/lightning
Published: 2026-01-12
Source: https://github.com/ElementsProject/lightning/commit/118e474637c55775a1ece42dbee4e34aac73fab3
Type: security-commit

## Details
askrene: fix payment crash

Changelog-Fixed: askrene: fix a plugin crash triggered during single path payments when a channel fees doesn't fit u32.

Signed-off-by: Lagrang3 <lagrang3@protonmail.com>

## Patch
### plugins/askrene/mcf.c
```diff
@@ -1157,11 +1157,8 @@ static void init_linear_network_single_path(
 					     c->half[half].base_fee,
 					     c->half[half].proportional_fee))
 				abort();
-			u32 fee_msat;
-			if (!amount_msat_to_u32(fee, &fee_msat))
-				continue;
 			(*arc_fee_cost)[arc.idx] =
-			    fee_msat +
+			    fee.millisatoshis + /* Raw: fee cost */
 			    params->delay_feefactor * c->half[half].delay;
 		}
 	}
```

### tests/test_askrene.py
```diff
@@ -1961,7 +1961,6 @@ def test_splice_dying_channel(node_factory, bitcoind):
     assert set([only_one(r['path'])['short_channel_id_dir'] for r in routes]) == set([pre_splice_scidd, post_splice_scidd])
 
 
-@unittest.skip
 def test_excessive_fee_cost(node_factory):
     """Produce a arc with very large fee cost that triggers an assertion in
     askrene's single path solver."""
```
