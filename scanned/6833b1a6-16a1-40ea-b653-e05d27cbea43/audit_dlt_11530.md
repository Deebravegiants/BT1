# [?] fix(x/distribution)!: can halt when historical rewards overflow (#5191)

## Summary
Severity: Unknown
Chain: Celestia
Component: celestiaorg/celestia-app
Published: 2025-07-08
Source: https://github.com/celestiaorg/celestia-app/commit/9c34cec467f5042a74d94e6855d72be0001244d2
Type: security-commit

## Details
fix(x/distribution)!: can halt when historical rewards overflow (#5191)

Closes https://github.com/celestiaorg/celestia-app/issues/5173

The [security
advisory](https://github.com/cosmos/cosmos-sdk/security/advisories/GHSA-p22h-3m2v-cmgh)
doesn't say anything about consensus breaking but the email announcement
says:

> The patch is state-breaking and will require a coordinated upgrade.

This doesn't impact Mainnet because it's still on celestia-app v3.x.
This does impact Arabica and Mocha but my opinion is that we should rush
a release out instead of doing another app version upgrade on Arabica
and Mocha.

## Patch
### go.mod
```diff
@@ -273,7 +273,7 @@ replace (
 	cosmossdk.io/x/upgrade => github.com/celestiaorg/cosmos-sdk/x/upgrade v0.1.0
 	// TODO: update to a v0.39.x release after that is created from celestia-core main branch.
 	github.com/cometbft/cometbft => github.com/celestiaorg/celestia-core v1.56.1-tm-v0.38.17
-	github.com/cosmos/cosmos-sdk => github.com/celestiaorg/cosmos-sdk v1.29.3-sdk-v0.50.12
+	github.com/cosmos/cosmos-sdk => github.com/celestiaorg/cosmos-sdk v1.29.4-sdk-v0.50.14
 	// goleveldb: canonical version
 	github.com/syndtr/goleveldb => github.com/syndtr/goleveldb v1.0.1-0.20210819022825-2ae1ddf74ef7
 	// celestia-core(v0.34.x): used for multiplexing abci v1 requests
```

### go.sum
```diff
@@ -355,8 +355,8 @@ github.com/celestiaorg/celestia-core v1.55.0-tm-v0.34.35 h1:FREwqZwPvYsodr1AqqEI
 github.com/celestiaorg/celestia-core v1.55.0-tm-v0.34.35/go.mod h1:SI38xqZZ4ccoAxszUJqsJ/a5rOkzQRijzHQQlLKkyUc=
 github.com/celestiaorg/celestia-core v1.56.1-tm-v0.38.17 h1:bbsnn4eyE0UG9benmUIdmv16i21vVdI0LJ35Wlb5SBc=
 github.com/celestiaorg/celestia-core v1.56.1-tm-v0.38.17/go.mod h1:jDJU+alpN4/MzC5Lz6+IsAYmvy8SrkD+jplk+C3W0Yo=
-github.com/celestiaorg/cosmos-sdk v1.29.3-sdk-v0.50.12 h1:ruVdAafsUzIGhas2qrf5cdweZA+WDxo9KUgRruJGUM0=
-github.com/celestiaorg/cosmos-sdk v1.29.3-sdk-v0.50.12/go.mod h1:clLEg7hWK0iJfiO1Vp71tcQ0vGbFzVsEcLxxnRobIZM=
+github.com/celestiaorg/cosmos-sdk v1.29.4-sdk-v0.50.14 h1:MBVJBZuJqZLyRgYkF4ONvtv6Ncn0LOB3XVKWqj3VDhQ=
+github.com/celestiaorg/cosmos-sdk v1.29.4-sdk-v0.50.14/go.mod h1:clLEg7hWK0iJfiO1Vp71tcQ0vGbFzVsEcLxxnRobIZM=
 github.com/celestiaorg/cosmos-sdk/x/upgrade v0.1.0 h1:+i3G5mP/kPgFEn83EEXGly29QDin2Gvdt0kgpmw/vTg=
 github.com/celestiaorg/cosmos-sdk/x/upgrade v0.1.0/go.mod h1:T4K9O18zQNKNpt4YvTL3lcUt4aKOEU05ZIFWVdQi3Ak=
 github.com/celestiaorg/go-square/v2 v2.3.0 h1:tVh6sZy1d2l5maVXUpc7eoTXdb3ptJVJt/U8z2XUWgQ=
```

### test/docker-e2e/go.mod
```diff
@@ -273,7 +273,7 @@ replace (
 
 	github.com/celestiaorg/celestia-app/v5 => ../..
 	github.com/cometbft/cometbft => github.com/celestiaorg/celestia-core v1.56.1-tm-v0.38.17
-	github.com/cosmos/cosmos-sdk => github.com/celestiaorg/cosmos-sdk v1.29.3-sdk-v0.50.12
+	github.com/cosmos/cosmos-sdk => github.com/celestiaorg/cosmos-sdk v1.29.4-sdk-v0.50.14
 
 	github.com/gogo/protobuf => github.com/gogo/protobuf v1.3.2
 	// goleveldb: canonical version
```

### test/docker-e2e/go.sum
```diff
@@ -346,8 +346,8 @@ github.com/bytedance/sonic/loader v0.2.4/go.mod h1:N8A3vUdtUebEY2/VQC0MyhYeKUFos
 github.com/casbin/casbin/v2 v2.1.2/go.mod h1:YcPU1XXisHhLzuxH9coDNf2FbKpjGlbCg3n9yuLkIJQ=
 github.com/celestiaorg/celestia-core v1.56.1-tm-v0.38.17 h1:bbsnn4eyE0UG9benmUIdmv16i21vVdI0LJ35Wlb5SBc=
 github.com/celestiaorg/celestia-core v1.56.1-tm-v0.38.17/go.mod h1:jDJU+alpN4/MzC5Lz6+IsAYmvy8SrkD+jplk+C3W0Yo=
-github.com/celestiaorg/cosmos-sdk v1.29.3-sdk-v0.50.12 h1:ruVdAafsUzIGhas2qrf5cdweZA+WDxo9KUgRruJGUM0=
-github.com/celestiaorg/cosmos-sdk v1.29.3-sdk-v0.50.12/go.mod h1:clLEg7hWK0iJfiO1Vp71tcQ0vGbFzVsEcLxxnRobIZM=
+github.com/celestiaorg/cosmos-sdk v1.29.4-sdk-v0.50.14 h1:MBVJBZuJqZLyRgYkF4ONvtv6Ncn0LOB3XVKWqj3VDhQ=
+github.com/celestiaorg/cosmos-sdk v1.29.4-sdk-v0.50.14/go.mod h1:clLEg7hWK0iJfiO1Vp71tcQ0vGbFzVsEcLxxnRobIZM=
 github.com/celestiaorg/cosmos-sdk/x/upgrade v0.1.0 h1:+i3G5mP/kPgFEn83EEXGly29QDin2Gvdt0kgpmw/vTg=
 github.com/celestiaorg/cosmos-sdk/x/upgrade v0.1.0/go.mod h1:T4K9O18zQNKNpt4YvTL3lcUt4aKOEU05ZIFWVdQi3Ak=
 github.com/celestiaorg/go-square/v2 v2.3.0 h1:tVh6sZy1d2l5maVXUpc7eoTXdb3ptJVJt/U8z2XUWgQ=
```

### test/interchain/go.mod
```diff
@@ -4,7 +4,7 @@ go 1.24.2
 
 require (
 	cosmossdk.io/math v1.4.0
-	github.com/cosmos/cosmos-sdk v0.50.13
+	github.com/cosmos/cosmos-sdk v0.50.14
 	github.com/strangelove-ventures/interchaintest/v8 v8.5.0
 	github.com/stretchr/testify v1.10.0
 	go.uber.org/zap v1.27.0
```

### test/interchain/go.sum
```diff
@@ -376,8 +376,8 @@ github.com/cosmos/cosmos-db v1.1.1 h1:FezFSU37AlBC8S98NlSagL76oqBRWq/prTPvFcEJNC
 github.com/cosmos/cosmos-db v1.1.1/go.mod h1:AghjcIPqdhSLP/2Z0yha5xPH3nLnskz81pBx3tcVSAw=
 github.com/cosmos/cosmos-proto v1.0.0-beta.5 h1:eNcayDLpip+zVLRLYafhzLvQlSmyab+RC5W7ZfmxJLA=
 github.com/cosmos/cosmos-proto v1.0.0-beta.5/go.mod h1:hQGLpiIUloJBMdQMMWb/4wRApmI9hjHH05nefC0Ojec=
-github.com/cosmos/cosmos-sdk v0.50.13 h1:xQ32hhzVy7agEe7behMdZN0ezWhPss3KoLZsF9KoBnw=
-github.com/cosmos/cosmos-sdk v0.50.13/go.mod h1:hrWEFMU1eoXqLJeE6VVESpJDQH67FS1nnMrQIjO2daw=
+github.com/cosmos/cosmos-sdk v0.50.14 h1:G8CtGHFWbExa+ZpVOVAb4kFmko/R30igsYOwyzRMtgY=
+github.com/cosmos/cosmos-sdk v0.50.14/go.mod h1:hrWEFMU1eoXqLJeE6VVESpJDQH67FS1nnMrQIjO2daw=
 github.com/cosmos/go-bip39 v0.0.0-20180819234021-555e2067c45d/go.mod h1:tSxLoYXyBmiFeKpvmq4dzayMdCjCnu8uqmCysIGBT2Y=
 github.com/cosmos/go-bip39 v1.0.0 h1:pcomnQdrdH22njcAatO0yWojsUnCO3y2tNoV1cb6hHY=
 github.com/cosmos/go-bip39 v1.0.0/go.mod h1:RNJv0H/pOIVgxw6KS7QeX2a0Uo0aKUlfhZ4xuwvCdJw=
```
