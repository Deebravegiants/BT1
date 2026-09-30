# [?] fix(primitives): Potential nil panic detected (#1601)

## Summary
Severity: Unknown
Chain: Berachain
Component: berachain/beacon-kit
Published: 2024-06-25
Source: https://github.com/berachain/beacon-kit/commit/34fa086f76f0d3dcf10918018ce6aba1d5170afb
Type: security-commit

## Details
fix(primitives): Potential nil panic detected (#1601)

## Patch
### mod/primitives/pkg/ssz/buffer.go
```diff
@@ -57,10 +57,6 @@ func getBytes(size int) *byteBuffer {
 		}
 		b.Bytes = b.Bytes[:size]
 	}
-	if cap(b.Bytes) < size {
-		b.Bytes = make([]common.Root, size)
-	}
-	b.Bytes = b.Bytes[:size]
 	return b
 }
 
```

### mod/primitives/pkg/ssz/merkleize.go
```diff
@@ -146,7 +146,9 @@ func MerkleizeVecComposite[
 		if err != nil {
 			return RootT{}, err
 		}
-		copy(htrs.Bytes[i][:], htr[:])
+		if htrs.Bytes != nil {
+			copy(htrs.Bytes[i][:], htr[:])
+		}
 	}
 	return Merkleize[U64T, RootT](htrs.Bytes)
 }
@@ -172,7 +174,11 @@ func MerkleizeListComposite[
 		if err != nil {
 			return RootT{}, err
 		}
-		copy(htrs.Bytes[i][:], htr[:])
+		if htrs.Bytes != nil {
+			copy(htrs.Bytes[i][:], htr[:])
+		} else {
+			return RootT{}, errors.New("htrs.Bytes is nil")
+		}
 	}
 	root, err := Merkleize[U64T, RootT](
 		htrs.Bytes,
```
