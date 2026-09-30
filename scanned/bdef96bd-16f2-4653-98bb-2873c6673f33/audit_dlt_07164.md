# [?] askrene: fix crash loading node bias with description

## Summary
Severity: Unknown
Chain: Bitcoin/Lightning
Component: ElementsProject/lightning
Published: 2026-08-18
Source: https://github.com/ElementsProject/lightning/commit/4681177d46e3f1d501bfc4476550415e6ce70002
Type: security-commit

## Details
askrene: fix crash loading node bias with description

load_node_bias() passed take(description) to two consecutive
set_node_bias() calls.  The first call's tal_strdup() consumes the
take (tal_resize_ + tal_steal), so the second take() was on freed
memory and we aborted in to_tal_hdr() with "Not a valid header"
while loading the layer at startup.  Since askrene is an important
plugin, lightningd shuts down and the node cannot restart at all.

The description is already a copy off tmpctx, so simply don't take()
it: set_node_bias() strdups it into the bias anyway.

With this, the test from the previous commit passes.

Fixes: #9433
Reported-by: endothermicdev
Changelog-Fixed: askrene: node failed to start (`exited before replying to init`) when a persistent layer contains a node bias with a description
Signed-off-by: Vincenzo Palazzo <vincenzopalazzodev@gmail.com>

## Patch
### plugins/askrene/layer.c
```diff
@@ -773,10 +773,10 @@ static void load_node_bias(struct plugin *plugin,
 				      &in_bias,
 				      &out_bias,
 				      &timestamp)) {
-		set_node_bias(layer, &node, take(description), in_bias,
+		set_node_bias(layer, &node, description, in_bias,
 			      /* relative = */ false,
 			      /* out dir = */ false, timestamp);
-		set_node_bias(layer, &node, take(description), out_bias,
+		set_node_bias(layer, &node, description, out_bias,
 			      /* relative = */ false,
 			      /* out dir = */ true, timestamp);
 	}
```

### tests/test_askrene.py
```diff
@@ -473,7 +473,6 @@ def test_node_bias_rpc(node_factory):
     assert listlayers == {"layers": [expect]}
 
 
-@pytest.mark.xfail(strict=True)
 def test_node_bias_persistence(node_factory):
     """Test node bias persistence."""
     # remove xpay, since it creates a layer!
```
