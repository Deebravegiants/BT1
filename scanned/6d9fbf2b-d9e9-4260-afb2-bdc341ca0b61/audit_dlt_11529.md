# [?] fix: panic due to nil limit (#5290)

## Summary
Severity: Unknown
Chain: Celestia
Component: celestiaorg/celestia-app
Published: 2025-07-23
Source: https://github.com/celestiaorg/celestia-app/commit/047d015c739033d664f9a06686dab3ba31ba1b4a
Type: security-commit

## Details
fix: panic due to nil limit (#5290)

Closes https://github.com/celestiaorg/celestia-app/issues/5279

## Patch
### go.mod
```diff
@@ -269,10 +269,9 @@ require (
 )
 
 replace (
-	// x/upgrade: v0.1.0
 	cosmossdk.io/x/upgrade => github.com/celestiaorg/cosmos-sdk/x/upgrade v0.1.0
 	// TODO: update to a v0.39.x release after that is created from celestia-core main branch.
-	github.com/cometbft/cometbft => github.com/celestiaorg/celestia-core v1.57.1-tm-v0.38.17
+	github.com/cometbft/cometbft => github.com/celestiaorg/celestia-core v1.57.2-tm-v0.38.17
 	github.com/cosmos/cosmos-sdk => github.com/celestiaorg/cosmos-sdk v1.29.4-sdk-v0.50.14
 	// goleveldb: canonical version
 	github.com/syndtr/goleveldb => github.com/syndtr/goleveldb v1.0.1-0.20210819022825-2ae1ddf74ef7
```

### go.sum
```diff
@@ -353,8 +353,8 @@ github.com/bytedance/sonic/loader v0.2.4/go.mod h1:N8A3vUdtUebEY2/VQC0MyhYeKUFos
 github.com/casbin/casbin/v2 v2.1.2/go.mod h1:YcPU1XXisHhLzuxH9coDNf2FbKpjGlbCg3n9yuLkIJQ=
 github.com/celestiaorg/celestia-core v1.55.0-tm-v0.34.35 h1:FREwqZwPvYsodr1AqqEIyW+VsBnwTzJNtC6NFdZX8rs=
 github.com/celestiaorg/celestia-core v1.55.0-tm-v0.34.35/go.mod h1:SI38xqZZ4ccoAxszUJqsJ/a5rOkzQRijzHQQlLKkyUc=
-github.com/celestiaorg/celestia-core v1.57.1-tm-v0.38.17 h1:mvzt/Jk/aBCe5d0733p7vQg+usjRRvF+nZtsvJmnr0s=
-github.com/celestiaorg/celestia-core v1.57.1-tm-v0.38.17/go.mod h1:jDJU+alpN4/MzC5Lz6+IsAYmvy8SrkD+jplk+C3W0Yo=
+github.com/celestiaorg/celestia-core v1.57.2-tm-v0.38.17 h1:bSE0PmkH6Fntf6ssVYLpnBHWYlhIRX7ebtpfBf18ly8=
+github.com/celestiaorg/celestia-core v1.57.2-tm-v0.38.17/go.mod h1:jDJU+alpN4/MzC5Lz6+IsAYmvy8SrkD+jplk+C3W0Yo=
 github.com/celestiaorg/cosmos-sdk v1.29.4-sdk-v0.50.14 h1:MBVJBZuJqZLyRgYkF4ONvtv6Ncn0LOB3XVKWqj3VDhQ=
 github.com/celestiaorg/cosmos-sdk v1.29.4-sdk-v0.50.14/go.mod h1:clLEg7hWK0iJfiO1Vp71tcQ0vGbFzVsEcLxxnRobIZM=
 github.com/celestiaorg/cosmos-sdk/x/upgrade v0.1.0 h1:+i3G5mP/kPgFEn83EEXGly29QDin2Gvdt0kgpmw/vTg=
```

### test/docker-e2e/go.mod
```diff
@@ -269,13 +269,10 @@ require (
 )
 
 replace (
-	// x/upgrade: v0.1.0
 	cosmossdk.io/x/upgrade => github.com/celestiaorg/cosmos-sdk/x/upgrade v0.1.0
-
 	github.com/celestiaorg/celestia-app/v5 => ../..
-	github.com/cometbft/cometbft => github.com/celestiaorg/celestia-core v1.56.1-tm-v0.38.17
+	github.com/cometbft/cometbft => github.com/celestiaorg/celestia-core v1.57.2-tm-v0.38.17
 	github.com/cosmos/cosmos-sdk => github.com/celestiaorg/cosmos-sdk v1.29.4-sdk-v0.50.14
-
 	github.com/gogo/protobuf => github.com/gogo/protobuf v1.3.2
 	// goleveldb: canonical version
 	github.com/syndtr/goleveldb => github.com/syndtr/goleveldb v1.0.1-0.20210819022825-2ae1ddf74ef7
```

### test/docker-e2e/go.sum
```diff
@@ -344,8 +344,8 @@ github.com/bytedance/sonic/loader v0.1.1/go.mod h1:ncP89zfokxS5LZrJxl5z0UJcsk4M4
 github.com/bytedance/sonic/loader v0.2.4 h1:ZWCw4stuXUsn1/+zQDqeE7JKP+QO47tz7QCNan80NzY=
 github.com/bytedance/sonic/loader v0.2.4/go.mod h1:N8A3vUdtUebEY2/VQC0MyhYeKUFosQU6FxH2JmUe6VI=
 github.com/casbin/casbin/v2 v2.1.2/go.mod h1:YcPU1XXisHhLzuxH9coDNf2FbKpjGlbCg3n9yuLkIJQ=
-github.com/celestiaorg/celestia-core v1.56.1-tm-v0.38.17 h1:bbsnn4eyE0UG9benmUIdmv16i21vVdI0LJ35Wlb5SBc=
-github.com/celestiaorg/celestia-core v1.56.1-tm-v0.38.17/go.mod h1:jDJU+alpN4/MzC5Lz6+IsAYmvy8SrkD+jplk+C3W0Yo=
+github.com/celestiaorg/celestia-core v1.57.2-tm-v0.38.17 h1:bSE0PmkH6Fntf6ssVYLpnBHWYlhIRX7ebtpfBf18ly8=
+github.com/celestiaorg/celestia-core v1.57.2-tm-v0.38.17/go.mod h1:jDJU+alpN4/MzC5Lz6+IsAYmvy8SrkD+jplk+C3W0Yo=
 github.com/celestiaorg/cosmos-sdk v1.29.4-sdk-v0.50.14 h1:MBVJBZuJqZLyRgYkF4ONvtv6Ncn0LOB3XVKWqj3VDhQ=
 github.com/celestiaorg/cosmos-sdk v1.29.4-sdk-v0.50.14/go.mod h1:clLEg7hWK0iJfiO1Vp71tcQ0vGbFzVsEcLxxnRobIZM=
 github.com/celestiaorg/cosmos-sdk/x/upgrade v0.1.0 h1:+i3G5mP/kPgFEn83EEXGly29QDin2Gvdt0kgpmw/vTg=
```
