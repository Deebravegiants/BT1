# [?] fix: patch comet bft (GHSA-hrhf-2vcr-ghch) (#1888)

## Summary
Severity: Unknown
Chain: Cronos
Component: crypto-org-chain/cronos
Published: 2025-10-15
Source: https://github.com/crypto-org-chain/cronos/commit/a755c37eb70519f57c1cb003eec4b6b606e3348f
Type: security-commit

## Details
fix: patch comet bft (GHSA-hrhf-2vcr-ghch) (#1888)

* patch comet bft

* add changelog

## Patch
### CHANGELOG.md
```diff
@@ -6,6 +6,7 @@
 * [#1872](https://github.com/crypto-org-chain/cronos/pull/1872) Support 4byteTracer for tracer
 * [#1875](https://github.com/crypto-org-chain/cronos/pull/1875) Support for preinstalls
 * [#1882](https://github.com/crypto-org-chain/cronos/pull/1882) Support for eip2935
+* [#1888](https://github.com/crypto-org-chain/cronos/pull/1888) Patch comet bft (GHSA-hrhf-2vcr-ghch)
 
 *Sep 4, 2025*
 
```

### go.mod
```diff
@@ -297,7 +297,7 @@ replace (
 	// Use cosmos keyring
 	github.com/99designs/keyring => github.com/cosmos/keyring v1.2.0
 	// v0.38.x
-	github.com/cometbft/cometbft => github.com/crypto-org-chain/cometbft v0.0.0-20250203071505-1964da4a0cac
+	github.com/cometbft/cometbft => github.com/crypto-org-chain/cometbft v0.0.0-20251014161156-b0e778b18408
 	// solves bug on pruning "version does not exist"
 	github.com/cosmos/iavl => github.com/cosmos/iavl v1.2.6
 	// dgrijalva/jwt-go is deprecated and doesn't receive security updates.
```

### go.sum
```diff
@@ -904,8 +904,8 @@ github.com/creack/pty v1.1.7/go.mod h1:lj5s0c3V2DBrqTV7llrYr5NG6My20zk30Fl46Y7Do
 github.com/creack/pty v1.1.9/go.mod h1:oKZEueFk5CKHvIhNR5MUki03XCEU+Q6VDXinZuGJ33E=
 github.com/crypto-org-chain/btree v0.0.0-20240406140148-2687063b042c h1:MOgfS4+FBB8cMkDE2j2VBVsbY+HCkPIu0YsJ/9bbGeQ=
 github.com/crypto-org-chain/btree v0.0.0-20240406140148-2687063b042c/go.mod h1:twD9XRA5jj9VUQGELzDO4HPQTNJsoWWfYEL+EUQ2cKY=
-github.com/crypto-org-chain/cometbft v0.0.0-20250203071505-1964da4a0cac h1:o09a/x43av8lYlJ0c8ChRU11iGYyqMvbeOz7skV6f6Y=
-github.com/crypto-org-chain/cometbft v0.0.0-20250203071505-1964da4a0cac/go.mod h1:khbgmtxbgwJfMqDmnGY4rl2sQpTdzpPb1f9nqnfpy1o=
+github.com/crypto-org-chain/cometbft v0.0.0-20251014161156-b0e778b18408 h1:7dfWkDRYCsguKrpd0t14nrZ3Xf/9aVHiQrWx5o0DCdo=
+github.com/crypto-org-chain/cometbft v0.0.0-20251014161156-b0e778b18408/go.mod h1:khbgmtxbgwJfMqDmnGY4rl2sQpTdzpPb1f9nqnfpy1o=
 github.com/crypto-org-chain/cosmos-sdk v0.50.6-0.20250424063720-28ea58ae20d8 h1:Sif0pGNc4C384OLucyQ7P/+KjYiJ6uDn8Cf8wR7MI+c=
 github.com/crypto-org-chain/cosmos-sdk v0.50.6-0.20250424063720-28ea58ae20d8/go.mod h1:JwwsMeZldLN20b72mmbWPY0EV9rs+v/12hRu1JFttvY=
 github.com/crypto-org-chain/cosmos-sdk/store v0.0.0-20241217090828-cfbca9fe8254 h1:NEgy0r3otU/O+0OAjMdEhbn4VotQlg+98hHbD7M23wU=
```

### gomod2nix.toml
```diff
@@ -194,8 +194,8 @@ schema = 3
     version = "v1.0.0"
     hash = "sha256-z/0E0NiEGo7zxM7d94ImgUf8P0/KG6hbP9T4Vuym4p0="
   [mod."github.com/cometbft/cometbft"]
-    version = "v0.0.0-20250203071505-1964da4a0cac"
-    hash = "sha256-69eQmjbxHnnXXC4wAVUFVY031fRzUSGeqbemzWylgzI="
+    version = "v0.0.0-20251014161156-b0e778b18408"
+    hash = "sha256-m2NPhw3gOXnWvVBud0zTMf1HfkTHkUZpsm1f9Goajwo="
     replaced = "github.com/crypto-org-chain/cometbft"
   [mod."github.com/cometbft/cometbft-db"]
     version = "v0.15.0"
```
