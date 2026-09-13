# [?] Fix out-of-bounds chunk index error in erasure coding (#12521)

## Summary
Severity: Unknown
Chain: Polkadot
Component: paritytech/polkadot-sdk
Published: 2026-07-15
Source: https://github.com/paritytech/polkadot-sdk/commit/35000d248860886d1b2fab8c79940e3356d02a36
Type: security-commit

## Details
Fix out-of-bounds chunk index error in erasure coding (#12521)

# Description

`reconstruct` in `polkadot-erasure-coding` allocated `received_shards`
with
length `n_validators` and then indexed it directly with the
caller-provided
`chunk_idx`. Any chunk index `>= n_validators` panicked with an
index-out-of-bounds instead of returning the already-defined
`Error::ChunkIndexOutOfBounds` variant.

This PR adds the missing bounds check so invalid indices are reported as
an
error rather than panicking.

Closes #12465

## Integration

`reconstruct` (and `reconstruct_v1`) now
return `Err(Error::ChunkIndexOutOfBounds { chunk_index, n_validators })`
for an
out-of-bounds chunk index where they previously panicked. The function
already
returns `Result<_, Error>` and the variant is already public, so there
is no API
or signature change — callers that propagate the `Result` need no
modification.

## Review Notes

The fix is a single guard in the chunk-consumption loop, placed
alongside the
existing `UnevenLength` check and before the indexing write:

```rust
if chunk_idx >= n_validators {
    return Err(Error::ChunkIndexOutOfBounds { chunk_index: chunk_idx, n_validators });
}

received_shards[chunk_idx] = Some(WrappedShard::new(chunk_data.to_vec()));
```

A regression test
(reconstruct_returns_error_on_out_of_bounds_chunk_index)
encodes data, then calls reconstruct with one valid index and one index
equal
to n_validators, asserting the ChunkIndexOutOfBounds error is returned
instead of panicking. The PoC from the isore]
because it expected a panic; once the function returns an error a direct
assert_eq! is sufficient, matching the exle.

### Checklist

- [x] My PR includes a detailed description and its two subsections
above.
- [x] My PR follows the labeling requirements
- [x] I have made corresponding changes table)
- [x] I have added tests that prove my fix is effective

---------

Co-authored-by: cmd[bot] <41898282+github-actions[bot]@users.noreply.github.com>

### polkadot/erasure-coding/src/lib.rs
```diff
@@ -231,6 +231,10 @@ where
 			return Err(Error::UnevenLength);
 		}
 
+		if chunk_idx >= n_validators {
+			return Err(Error::ChunkIndexOutOfBounds { chunk_index: chunk_idx, n_validators });
+		}
+
 		received_shards[chunk_idx] = Some(WrappedShard::new(chunk_data.to_vec()));
 	}
 
@@ -417,6 +421,23 @@ mod tests {
 		assert_eq!(reconstructed, Err(Error::NotEnoughValidators));
 	}
 
+	#[test]
+	fn reconstruct_returns_error_on_out_of_bounds_chunk_index() {
+		let n_validators = 10;
+		let pov = PoV { block_data: BlockData((0..255).collect()) };
+		let available_data = AvailableData { pov: pov.into(), validation_data: Default::default() };
+		let chunks = obtain_chunks(n_validators, &available_data).unwrap();
+
+		let reconstructed: Result<AvailableData, _> = reconstruct(
+			n_validators,
+			[(&*chunks[0], 0), (&*chunks[1], n_validators)].iter().cloned(),
+		);
+		assert_eq!(
+			reconstructed,
+			Err(Error::ChunkIndexOutOfBounds { chunk_index: n_validators, n_validators })
+		);
+	}
+
 	fn generate_trie_and_generate_proofs(magnitude: u32) {
 		let n_validators = 2_u32.pow(magnitude) as usize;
 		let pov = PoV { block_data: BlockData(vec![2; n_validators / KEY_INDEX_NIBBLE_SIZE]) };
```

### prdoc/pr_12521.prdoc
```diff
@@ -0,0 +1,29 @@
+title: Fix out-of-bounds chunk index error in erasure coding
+doc:
+- audience: Node Dev
+  description: "# Description\n\n`reconstruct` in `polkadot-erasure-coding` allocated\
+    \ `received_shards` with\nlength `n_validators` and then indexed it directly with\
+    \ the caller-provided\n`chunk_idx`. Any chunk index `>= n_validators` panicked\
+    \ with an\nindex-out-of-bounds instead of returning the already-defined\n`Error::ChunkIndexOutOfBounds`\
+    \ variant.\n\nThis PR adds the missing bounds check so invalid indices are reported\
+    \ as an\nerror rather than panicking.\n\nCloses #12465\n\n## Integration\n\n`reconstruct`\
+    \ (and `reconstruct_v1`) now\nreturn `Err(Error::ChunkIndexOutOfBounds { chunk_index,\
+    \ n_validators })` for an\nout-of-bounds chunk index where they previously panicked.\
+    \ The function already\nreturns `Result<_, Error>` and the variant is already\
+    \ public, so there is no API\nor signature change \u2014 callers that propagate\
+    \ the `Result` need no modification.\n\n## Review Notes\n\nThe fix is a single\
+    \ guard in the chunk-consumption loop, placed alongside the\nexisting `UnevenLength`\
+    \ check and before the indexing write:\n\n```rust\nif chunk_idx >= n_validators\
+    \ {\n    return Err(Error::ChunkIndexOutOfBounds { chunk_index: chunk_idx, n_validators\
+    \ });\n}\n\nreceived_shards[chunk_idx] = Some(WrappedShard::new(chunk_data.to_vec()));\n\
+    ```\n\nA regression test (reconstruct_returns_error_on_out_of_bounds_chunk_index)\n\
+    encodes data, then calls reconstruct with one valid index and one index equal\n\
+    to n_validators, asserting the ChunkIndexOutOfBounds error is returned\ninstead\
+    \ of panicking. The PoC from the isore]\nbecause it expected a panic; once the\
+    \ function returns an error a direct\nassert_eq! is sufficient, matching the exle.\n\
+    \n### Checklist\n\n- [x] My PR includes a detailed description and its two subsections\
+    \ above.\n- [x] My PR follows the labeling requirements\n- [x] I have made corresponding\
+    \ changes table)\n- [x] I have added tests that prove my fix is effective"
+crates:
+- name: polkadot-erasure-coding
+  bump: patch
```
