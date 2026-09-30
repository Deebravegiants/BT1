# [?] Update to IAVL v0.19.4 to fix panic on fastnode flag switch (#1380)

## Summary
Severity: Unknown
Chain: Kava
Component: Kava-Labs/kava
Published: 2022-11-03
Source: https://github.com/Kava-Labs/kava/commit/6a12f2a9c9b7d7c4424c2c7b1435574f49ecdb61
Type: security-commit

## Details
Update to IAVL v0.19.4 to fix panic on fastnode flag switch (#1380)

Fixes a panic with fast node is switched off

## Patch
### go.mod
```diff
@@ -45,7 +45,7 @@ require (
 	github.com/confio/ics23/go v0.7.0 // indirect
 	github.com/cosmos/btcutil v1.0.4 // indirect
 	github.com/cosmos/go-bip39 v1.0.0 // indirect
-	github.com/cosmos/iavl v0.19.3 // indirect
+	github.com/cosmos/iavl v0.19.4 // indirect
 	github.com/cosmos/ledger-cosmos-go v0.11.1 // indirect
 	github.com/cosmos/ledger-go v0.9.2 // indirect
 	github.com/creachadair/taskgroup v0.3.2 // indirect
```

### go.sum
```diff
@@ -197,6 +197,8 @@ github.com/cosmos/go-bip39 v1.0.0 h1:pcomnQdrdH22njcAatO0yWojsUnCO3y2tNoV1cb6hHY
 github.com/cosmos/go-bip39 v1.0.0/go.mod h1:RNJv0H/pOIVgxw6KS7QeX2a0Uo0aKUlfhZ4xuwvCdJw=
 github.com/cosmos/iavl v0.19.3 h1:cESO0OwTTxQm5rmyESKW+zESheDUYI7CcZDWWDwnuxg=
 github.com/cosmos/iavl v0.19.3/go.mod h1:X9PKD3J0iFxdmgNLa7b2LYWdsGd90ToV5cAONApkEPw=
+github.com/cosmos/iavl v0.19.4 h1:t82sN+Y0WeqxDLJRSpNd8YFX5URIrT+p8n6oJbJ2Dok=
+github.com/cosmos/iavl v0.19.4/go.mod h1:X9PKD3J0iFxdmgNLa7b2LYWdsGd90ToV5cAONApkEPw=
 github.com/cosmos/ibc-go/v3 v3.3.1 h1:i8o3iPSPN8fr7AjCPQnHEKz/VfeMrxc8mjvgAw6txWk=
 github.com/cosmos/ibc-go/v3 v3.3.1/go.mod h1:V1nliDk/5q5KWr0mup7M76oN4SY0IOU371SKbCV2wN0=
 github.com/cosmos/keyring v1.1.7-0.20210622111912-ef00f8ac3d76 h1:DdzS1m6o/pCqeZ8VOAit/gyATedRgjvkVI+UCrLpyuU=
```
