# [?] upgrade cosmos-sdk and cometbft for security patch GHSA-hrhf-2vcr-ghch (#3148)

## Summary
Severity: Unknown
Chain: dYdX
Component: dydxprotocol/v4-chain
Published: 2025-10-14
Source: https://github.com/dydxprotocol/v4-chain/commit/fb3838ad578c27c36fcd67a4639dfd72f2aa37e2
Type: security-commit

## Details
upgrade cosmos-sdk and cometbft for security patch GHSA-hrhf-2vcr-ghch (#3148)

## Patch
### protocol/go.mod
```diff
@@ -470,13 +470,13 @@ replace (
 	// Use dYdX fork of Cosmos SDK/store
 	cosmossdk.io/store => github.com/dydxprotocol/cosmos-sdk/store v1.0.3-0.20240326192503-dd116391188d
 	// Use dYdX fork of CometBFT
-	github.com/cometbft/cometbft => github.com/dydxprotocol/cometbft v0.38.6-0.20250917222732-ee7f1a0892c4
+	github.com/cometbft/cometbft => github.com/dydxprotocol/cometbft v0.38.6-0.20251014202517-0235a938b029
 	// Fixes the issue that `tx_search` resolves to a single entry, due to an cometbft-db interface
 	// change in v0.13.0+.
 	// TODO(CT-1343): Remove and fix properly by backporting upstream fix to cometbft fork.
 	github.com/cometbft/cometbft-db => github.com/cometbft/cometbft-db v0.12.0
 	// Use dYdX fork of Cosmos SDK
-	github.com/cosmos/cosmos-sdk => github.com/dydxprotocol/cosmos-sdk v0.50.6-0.20250918154803-8e8ecbb19aa4
+	github.com/cosmos/cosmos-sdk => github.com/dydxprotocol/cosmos-sdk v0.50.6-0.20251014211237-3a1ba0aabac3
 	github.com/cosmos/iavl => github.com/dydxprotocol/iavl v1.1.1-0.20240509161911-1c8b8e787e85
 )
 
```

### protocol/go.sum
```diff
@@ -956,10 +956,10 @@ github.com/dustin/go-humanize v1.0.1 h1:GzkhY7T5VNhEkwH0PVJgjz+fX1rhBrR7pRT3mDkp
 github.com/dustin/go-humanize v1.0.1/go.mod h1:Mu1zIs6XwVuF/gI1OepvI0qD18qycQx+mFykh5fBlto=
 github.com/dvsekhvalnov/jose2go v1.6.0 h1:Y9gnSnP4qEI0+/uQkHvFXeD2PLPJeXEL+ySMEA2EjTY=
 github.com/dvsekhvalnov/jose2go v1.6.0/go.mod h1:QsHjhyTlD/lAVqn/NSbVZmSCGeDehTB/mPZadG+mhXU=
-github.com/dydxprotocol/cometbft v0.38.6-0.20250917222732-ee7f1a0892c4 h1:hxWJ4ypVQmJe7mCRwpezCPJ+xIvnKbIQeDqMCzV5w4g=
-github.com/dydxprotocol/cometbft v0.38.6-0.20250917222732-ee7f1a0892c4/go.mod h1:XSQX1hQbr54qaJb4/5YNNZGXkAQHHa6bi/KMcN1SQ7w=
-github.com/dydxprotocol/cosmos-sdk v0.50.6-0.20250918154803-8e8ecbb19aa4 h1:jPMFeAox8YwIjUqxabNV/qFuf/EQlTemtTSCShOxMho=
-github.com/dydxprotocol/cosmos-sdk v0.50.6-0.20250918154803-8e8ecbb19aa4/go.mod h1:RFE4a5qI7zc42tja8BGBZ3HNSosygF9WWyjLcyr2bFg=
+github.com/dydxprotocol/cometbft v0.38.6-0.20251014202517-0235a938b029 h1:jgRwHeeMpPahMyWUvBT0TIdAo7M9y6CXLzF7ZZzYstg=
+github.com/dydxprotocol/cometbft v0.38.6-0.20251014202517-0235a938b029/go.mod h1:XSQX1hQbr54qaJb4/5YNNZGXkAQHHa6bi/KMcN1SQ7w=
+github.com/dydxprotocol/cosmos-sdk v0.50.6-0.20251014211237-3a1ba0aabac3 h1:VzjChSIDsDua0WjFoHb+bqodgeAMBPsflNS7ot14TQU=
+github.com/dydxprotocol/cosmos-sdk v0.50.6-0.20251014211237-3a1ba0aabac3/go.mod h1:PqtaF8C4fKHmDIvrdc7GBpZKsRkjihCJxq0gOlt2k98=
 github.com/dydxprotocol/cosmos-sdk/store v1.0.3-0.20240326192503-dd116391188d h1:HgLu1FD2oDFzlKW6/+SFXlH5Os8cwNTbplQIrQOWx8w=
 github.com/dydxprotocol/cosmos-sdk/store v1.0.3-0.20240326192503-dd116391188d/go.mod h1:zMcD3hfNwd0WMTpdRUhS3QxoCoEtBXWeoKsu3iaLBbQ=
 github.com/dydxprotocol/iavl v1.1.1-0.20240509161911-1c8b8e787e85 h1:5B/yGZyTBX/OZASQQMnk6Ms/TZja56MYd8OBaVc0Mho=
```
