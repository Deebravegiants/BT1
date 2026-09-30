# [?] fix: nil pointer panic when store don't exists in historical version (#20425)

## Summary
Severity: Unknown
Chain: Cosmos
Component: cosmos/cosmos-sdk
Published: 2024-05-20
Source: https://github.com/cosmos/cosmos-sdk/commit/1f06f5bec67e76843ceb00502a814b2a87e81d6b
Type: security-commit

## Details
fix: nil pointer panic when store don't exists in historical version (#20425)

## Patch
### store/CHANGELOG.md
```diff
@@ -23,6 +23,12 @@ Ref: https://keepachangelog.com/en/1.0.0/
 
 # Changelog
 
+## [Unreleased]
+
+### Bug Fixes
+
+* (store) [#20425](https://github.com/cosmos/cosmos-sdk/pull/20425) Fix nil pointer panic when query historical state where a new store don't exist.
+
 ## v1.1.0 (March 20, 2024)
 
 ### Improvements
```

### store/rootmulti/store.go
```diff
@@ -607,6 +607,10 @@ func (rs *Store) CacheMultiStoreWithVersion(version int64) (types.CacheMultiStor
 				if storeInfos[key.Name()] {
 					return nil, err
 				}
+
+				// If the store donesn't exist at this version, create a dummy one to prevent
+				// nil pointer panic in newer query APIs.
+				cacheStore = dbadapter.Store{DB: dbm.NewMemDB()}
 			}
 
 		default:
```

### store/rootmulti/store_test.go
```diff
@@ -100,16 +100,19 @@ func TestCacheMultiStoreWithVersion(t *testing.T) {
 	require.Equal(t, kvStore.Get(k), v)
 
 	// add new module stores (store4 and store5) to multi stores and commit
-	ms.MountStoreWithDB(types.NewKVStoreKey("store4"), types.StoreTypeIAVL, nil)
-	ms.MountStoreWithDB(types.NewKVStoreKey("store5"), types.StoreTypeIAVL, nil)
+	key4, key5 := types.NewKVStoreKey("store4"), types.NewKVStoreKey("store5")
+	ms.MountStoreWithDB(key4, types.StoreTypeIAVL, nil)
+	ms.MountStoreWithDB(key5, types.StoreTypeIAVL, nil)
 	err = ms.LoadLatestVersionAndUpgrade(&types.StoreUpgrades{Added: []string{"store4", "store5"}})
 	require.NoError(t, err)
 	ms.Commit()
 
 	// cache multistore of version before adding store4 should works
-	_, err = ms.CacheMultiStoreWithVersion(1)
+	cms2, err := ms.CacheMultiStoreWithVersion(1)
 	require.NoError(t, err)
 
+	require.Empty(t, cms2.GetKVStore(key4).Get([]byte("key")))
+
 	// require we cannot commit (write) to a cache-versioned multi-store
 	require.Panics(t, func() {
 		kvStore.Set(k, []byte("newValue"))
```
