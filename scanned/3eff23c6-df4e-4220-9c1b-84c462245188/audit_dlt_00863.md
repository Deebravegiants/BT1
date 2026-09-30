# [?] fix(tracing): fix ZktrieTracer race condition (#356)

## Summary
Severity: Unknown
Chain: Scroll
Component: scroll-tech/go-ethereum
Published: 2023-06-07
Source: https://github.com/scroll-tech/go-ethereum/commit/4867699afa29ecf900bf65221e26b5655ebbc539
Type: security-commit

## Details
fix(tracing): fix ZktrieTracer race condition (#356)

* fix race condition of zktrie tracer

* Update version.go

---------

Co-authored-by: HAOYUatHZ <37070449+HAOYUatHZ@users.noreply.github.com>

## Patch
### eth/tracers/api_blocktrace.go
```diff
@@ -345,7 +345,7 @@ func (api *API) getTxResult(env *traceEnv, state *state.StateDB, index int, bloc
 				m = make(map[string][]hexutil.Bytes)
 				env.StorageProofs[addrStr] = m
 				if zktrieTracer.Available() {
-					env.zkTrieTracer[addrStr] = zktrieTracer
+					env.zkTrieTracer[addrStr] = state.NewProofTracer(trie)
 				}
 			} else if _, existed := m[keyStr]; existed {
 				// still need to touch tracer for deletion
```

### params/version.go
```diff
@@ -24,7 +24,7 @@ import (
 const (
 	VersionMajor = 4         // Major version component of the current release
 	VersionMinor = 0         // Minor version component of the current release
-	VersionPatch = 3         // Patch version component of the current release
+	VersionPatch = 4         // Patch version component of the current release
 	VersionMeta  = "sepolia" // Version metadata to append to the version string
 )
 
```
