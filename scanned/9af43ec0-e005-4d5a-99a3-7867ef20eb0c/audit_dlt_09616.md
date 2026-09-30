# [?] fix non-determinism test in sim_test.go (#1739)

## Summary
Severity: Unknown
Chain: Cosmos Hub
Component: cosmos/gaia
Published: 2022-09-13
Source: https://github.com/cosmos/gaia/commit/599984318ee90f8624a3ca8155187abf27e6a1df
Type: security-commit

## Details
fix non-determinism test in sim_test.go (#1739)

* fix non-determinism test in sim_test.go

## Patch
### .github/workflows/release-sims.yml
```diff
@@ -65,7 +65,7 @@ jobs:
       - uses: actions/checkout@v3
       - uses: actions/setup-go@v3.0.0
         with:
-          go-version: 1.16
+          go-version: 1.18
       - uses: technote-space/get-diff-action@v6.0.1
         with:
           PATTERNS: |
```

### .github/workflows/sim-label.yml
```diff
@@ -33,7 +33,7 @@ jobs:
       - uses: actions/checkout@v2.4.0
       - uses: actions/setup-go@v3.0.0
         with:
-          go-version: 1.16
+          go-version: 1.18
       - uses: actions/cache@v3.0.8
         with:
           path: ~/go/bin
```

### app/sim_test.go
```diff
@@ -107,7 +107,7 @@ func TestAppStateDeterminism(t *testing.T) {
 			}
 
 			db := dbm.NewMemDB()
-			app := gaia.NewGaiaApp(logger, db, nil, true, map[int64]bool{}, gaia.DefaultNodeHome, simapp.FlagPeriodValue, params.MakeTestEncodingConfig(), simapp.EmptyAppOptions{}, interBlockCacheOpt())
+			app := gaia.NewGaiaApp(logger, db, nil, true, map[int64]bool{}, gaia.DefaultNodeHome, simapp.FlagPeriodValue, gaia.MakeTestEncodingConfig(), EmptyAppOptions{}, interBlockCacheOpt())
 
 			fmt.Printf(
 				"running non-determinism simulation; seed %d: %d/%d, attempt: %d/%d\n",
```
