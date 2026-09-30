# [?] fix(store): avoid panic when store not exists in historical version (port: #20425) (#24549)

## Summary
Severity: Unknown
Chain: Cosmos
Component: cosmos/cosmos-sdk
Published: 2025-05-15
Source: https://github.com/cosmos/cosmos-sdk/commit/7b7f3a24929931c34e627927493758a4998404e2
Type: security-commit

## Details
fix(store): avoid panic when store not exists in historical version (port: #20425) (#24549)

Co-authored-by: yihuang <huang@crypto.com>
Co-authored-by: Alex | Interchain Labs <alex@interchainlabs.io>

## Patch
### store/CHANGELOG.md
```diff
@@ -23,6 +23,12 @@ Ref: https://keepachangelog.com/en/1.0.0/
 
 # Changelog
 
+## [Unreleased]
+
+### Bug Fixes
+
+* [#20425](https://github.com/cosmos/cosmos-sdk/pull/20425) Fix nil pointer panic when querying historical state where a new store does not exist.
+
 ## v1.1.2 (March 31, 2025)
 
 ### Bug Fixes
```

### store/rootmulti/store.go
```diff
@@ -627,6 +627,10 @@ func (rs *Store) CacheMultiStoreWithVersion(version int64) (types.CacheMultiStor
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
@@ -120,6 +120,26 @@ func TestCacheMultiStoreWithVersion(t *testing.T) {
 	})
 }
 
+func TestCacheMultiStoreWithVersionStoreNotExist(t *testing.T) {
+	db := dbm.NewMemDB()
+	ms := newMultiStoreWithMounts(db, pruningtypes.NewPruningOptions(pruningtypes.PruningNothing))
+	err := ms.LoadLatestVersion()
+	require.Nil(t, err)
+	cID := ms.Commit()
+	require.Equal(t, int64(1), cID.Version)
+	// add new module stores (store4 and store5) to multi stores and commit
+	key4, key5 := types.NewKVStoreKey("store4"), types.NewKVStoreKey("store5")
+	ms.MountStoreWithDB(key4, types.StoreTypeIAVL, nil)
+	ms.MountStoreWithDB(key5, types.StoreTypeIAVL, nil)
+	err = ms.LoadLatestVersionAndUpgrade(&types.StoreUpgrades{Added: []string{"store4", "store5"}})
+	require.NoError(t, err)
+	ms.Commit()
+	// cache multistore of version before adding store4 should works
+	cms2, err := ms.CacheMultiStoreWithVersion(1)
+	require.NoError(t, err)
+	require.Empty(t, cms2.GetKVStore(key4).Get([]byte("key")))
+}
+
 func TestHashStableWithEmptyCommit(t *testing.T) {
 	var db dbm.DB = dbm.NewMemDB()
 	ms := newMultiStoreWithMounts(db, pruningtypes.NewPruningOptions(pruningtypes.PruningNothing))
```
