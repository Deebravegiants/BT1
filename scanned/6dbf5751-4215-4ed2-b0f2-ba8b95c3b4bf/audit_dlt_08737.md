# [?] fix(api): eth_getProof crash (#1159)

## Summary
Severity: Unknown
Chain: Scroll
Component: scroll-tech/go-ethereum
Published: 2025-03-26
Source: https://github.com/scroll-tech/go-ethereum/commit/24757865c6bbd9becb0256e97e8492d1f73987d9
Type: security-commit

## Details
fix(api): eth_getProof crash (#1159)

* fix(api): eth_getProof crash

* return PoseidonCodeHash for zktrie

* fix

## Patch
### internal/ethapi/api.go
```diff
@@ -692,7 +692,6 @@ func (s *PublicBlockChainAPI) GetProof(ctx context.Context, address common.Addre
 		storageHash = types.EmptyRootHash
 	}
 	keccakCodeHash := state.GetKeccakCodeHash(address)
-	poseidonCodeHash := state.GetPoseidonCodeHash(address)
 	storageProof := make([]StorageResult, len(storageKeys))
 
 	// if we have a storageTrie, (which means the account exists), we can update the storagehash
@@ -701,7 +700,6 @@ func (s *PublicBlockChainAPI) GetProof(ctx context.Context, address common.Addre
 	} else {
 		// no storageTrie means the account does not exist, so the codeHash is the hash of an empty bytearray.
 		keccakCodeHash = codehash.EmptyKeccakCodeHash
-		poseidonCodeHash = codehash.EmptyPoseidonCodeHash
 	}
 
 	// create the proof for the storageKeys
@@ -723,17 +721,26 @@ func (s *PublicBlockChainAPI) GetProof(ctx context.Context, address common.Addre
 		return nil, proofErr
 	}
 
-	return &AccountResult{
-		Address:          address,
-		AccountProof:     toHexSlice(accountProof),
-		Balance:          (*hexutil.Big)(state.GetBalance(address)),
-		KeccakCodeHash:   keccakCodeHash,
-		PoseidonCodeHash: poseidonCodeHash,
-		CodeSize:         hexutil.Uint64(state.GetCodeSize(address)),
-		Nonce:            hexutil.Uint64(state.GetNonce(address)),
-		StorageHash:      storageHash,
-		StorageProof:     storageProof,
-	}, state.Error()
+	result := &AccountResult{
+		Address:        address,
+		AccountProof:   toHexSlice(accountProof),
+		Balance:        (*hexutil.Big)(state.GetBalance(address)),
+		KeccakCodeHash: keccakCodeHash,
+		CodeSize:       hexutil.Uint64(state.GetCodeSize(address)),
+		Nonce:          hexutil.Uint64(state.GetNonce(address)),
+		StorageHash:    storageHash,
+		StorageProof:   storageProof,
+	}
+
+	if state.IsZktrie() {
+		if storageTrie != nil {
+			result.PoseidonCodeHash = state.GetPoseidonCodeHash(address)
+		} else {
+			result.PoseidonCodeHash = codehash.EmptyPoseidonCodeHash
+		}
+	}
+
+	return result, state.Error()
 }
 
 // GetHeaderByNumber returns the requested canonical block header.
```

### params/version.go
```diff
@@ -24,7 +24,7 @@ import (
 const (
 	VersionMajor = 5         // Major version component of the current release
 	VersionMinor = 8         // Minor version component of the current release
-	VersionPatch = 32        // Patch version component of the current release
+	VersionPatch = 33        // Patch version component of the current release
 	VersionMeta  = "mainnet" // Version metadata to append to the version string
 )
 
```
