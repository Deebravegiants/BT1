# [?] fix: non-deterministic JSON in IBC acks again (#4405)

## Summary
Severity: Unknown
Chain: Celestia
Component: celestiaorg/celestia-app
Published: 2025-03-13
Source: https://github.com/celestiaorg/celestia-app/commit/62326e8cb0fbd835b2ae56815a8227f1da0d5dc1
Type: security-commit

## Details
fix: non-deterministic JSON in IBC acks again (#4405)

Addresses
https://github.com/cosmos/ibc-go/security/advisories/GHSA-4wf3-5qj9-368v

## Patch
### go.mod
```diff
@@ -257,8 +257,8 @@ require (
 
 replace (
 	github.com/cosmos/cosmos-sdk => github.com/celestiaorg/cosmos-sdk v1.27.0-sdk-v0.46.16
-	// Replace IBC with celestiaorg fork which includes a fix for https://github.com/cosmos/ibc-go/security/advisories/GHSA-jg6f-48ff-5xrw
-	github.com/cosmos/ibc-go/v6 => github.com/celestiaorg/ibc-go/v6 v6.2.3
+	// Replace IBC with celestiaorg fork which includes fixes for security vulnerabilities.
+	github.com/cosmos/ibc-go/v6 => github.com/celestiaorg/ibc-go/v6 v6.2.4
 	github.com/gogo/protobuf => github.com/regen-network/protobuf v1.3.3-alpha.regen.1
 	github.com/syndtr/goleveldb => github.com/syndtr/goleveldb v1.0.1-0.20210819022825-2ae1ddf74ef7
 	github.com/tendermint/tendermint => github.com/celestiaorg/celestia-core v1.49.1-tm-v0.34.35
```

### go.sum
```diff
@@ -326,8 +326,8 @@ github.com/celestiaorg/go-square v1.1.1 h1:Cy3p8WVspVcyOqHM8BWFuuYPwMitO1pYGe+Im
 github.com/celestiaorg/go-square v1.1.1/go.mod h1:1EXMErhDrWJM8B8V9hN7dqJ2kUTClfwdqMOmF9yQUa0=
 github.com/celestiaorg/go-square/v2 v2.1.0 h1:ECIvYEeHIWiIJGDCJxQNtzqm5DmnBly7XGhSpLsl+Lw=
 github.com/celestiaorg/go-square/v2 v2.1.0/go.mod h1:n3ztrh8CBjWOD6iWYMo3pPOlQIgzLK9yrnqMPcNo6g8=
-github.com/celestiaorg/ibc-go/v6 v6.2.3 h1:INxacgOrRbPLPQVzbGA4QMDdcSLic6Ff5tf3fye3w/E=
-github.com/celestiaorg/ibc-go/v6 v6.2.3/go.mod h1:XLsARy4Y7+GtAqzMcxNdlQf6lx+ti1e8KcMGv5NIK7A=
+github.com/celestiaorg/ibc-go/v6 v6.2.4 h1:S9jH7e+faYWF9PgDQAQnHxgm+FeDWTKcOF99Zez40bA=
+github.com/celestiaorg/ibc-go/v6 v6.2.4/go.mod h1:XLsARy4Y7+GtAqzMcxNdlQf6lx+ti1e8KcMGv5NIK7A=
 github.com/celestiaorg/knuu v0.16.3 h1:ORmcBoSW+67iPKF0yIGKwWMefphk5hvy08KklmCT0aw=
 github.com/celestiaorg/knuu v0.16.3/go.mod h1:nB7IGCR984YKEDW+j5xHPOidYfbO4DoZI1rDKijvF5E=
 github.com/celestiaorg/merkletree v0.0.0-20210714075610-a84dc3ddbbe4 h1:CJdIpo8n5MFP2MwK0gSRcOVlDlFdQJO1p+FqdxYzmvc=
```

### test/interchain/go.mod
```diff
@@ -225,8 +225,8 @@ replace (
 // These replace statements were inspired by celestia-app.
 replace (
 	github.com/cosmos/cosmos-sdk => github.com/celestiaorg/cosmos-sdk v1.27.0-sdk-v0.46.16
-	// Replace IBC with celestiaorg fork which includes a fix for https://github.com/cosmos/ibc-go/security/advisories/GHSA-jg6f-48ff-5xrw
-	github.com/cosmos/ibc-go/v6 => github.com/celestiaorg/ibc-go/v6 v6.2.3
+	// Replace IBC with celestiaorg fork which includes fixes for security vulnerabilities.
+	github.com/cosmos/ibc-go/v6 => github.com/celestiaorg/ibc-go/v6 v6.2.4
 	github.com/docker/docker => github.com/docker/docker v24.0.1+incompatible
 	github.com/gogo/protobuf => github.com/regen-network/protobuf v1.3.3-alpha.regen.1
 	github.com/syndtr/goleveldb => github.com/syndtr/goleveldb v1.0.1-0.20210819022825-2ae1ddf74ef7
```

### test/interchain/go.sum
```diff
@@ -253,8 +253,8 @@ github.com/celestiaorg/celestia-core v1.49.1-tm-v0.34.35 h1:Fgm7Wj+378S0ktzpWiuI
 github.com/celestiaorg/celestia-core v1.49.1-tm-v0.34.35/go.mod h1:SI38xqZZ4ccoAxszUJqsJ/a5rOkzQRijzHQQlLKkyUc=
 github.com/celestiaorg/cosmos-sdk v1.27.0-sdk-v0.46.16 h1:qxWiGrDEcg4FzVTpIXU/v3wjP7q1Lz4AMhSBBRABInU=
 github.com/celestiaorg/cosmos-sdk v1.27.0-sdk-v0.46.16/go.mod h1:W30mNt3+2l516HVR8Gt9+Gf4qOrWC9/x18MTEx2GljE=
-github.com/celestiaorg/ibc-go/v6 v6.2.3 h1:INxacgOrRbPLPQVzbGA4QMDdcSLic6Ff5tf3fye3w/E=
-github.com/celestiaorg/ibc-go/v6 v6.2.3/go.mod h1:XLsARy4Y7+GtAqzMcxNdlQf6lx+ti1e8KcMGv5NIK7A=
+github.com/celestiaorg/ibc-go/v6 v6.2.4 h1:S9jH7e+faYWF9PgDQAQnHxgm+FeDWTKcOF99Zez40bA=
+github.com/celestiaorg/ibc-go/v6 v6.2.4/go.mod h1:XLsARy4Y7+GtAqzMcxNdlQf6lx+ti1e8KcMGv5NIK7A=
 github.com/celestiaorg/nmt v0.23.0 h1:cfYy//hL1HeDSH0ub3CPlJuox5U5xzgg4JGZrw23I/I=
 github.com/celestiaorg/nmt v0.23.0/go.mod h1:kYfIjRq5rmA2mJnv41GLWkxn5KyLNPlma3v5Q68rHdI=
 github.com/cenkalti/backoff v2.2.1+incompatible h1:tNowT99t7UNflLxfYYSlKYsBpXdEet03Pg2g16Swow4=
```
