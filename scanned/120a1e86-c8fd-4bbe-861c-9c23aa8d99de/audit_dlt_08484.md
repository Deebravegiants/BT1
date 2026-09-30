# [?] [EVM] fix mempool removal panic (#1608)

## Summary
Severity: Unknown
Chain: Sei
Component: sei-protocol/sei-chain
Published: 2024-04-30
Source: https://github.com/sei-protocol/sei-chain/commit/dd2e61d834aca643b7e5d6ba7d13dd8ff8282348
Type: security-commit

## Details
[EVM] fix mempool removal panic (#1608)

fix mempool removal panic

## Patch
### go.mod
```diff
@@ -346,15 +346,15 @@ require (
 replace (
 	github.com/CosmWasm/wasmd => github.com/sei-protocol/sei-wasmd v0.1.2
 	github.com/confio/ics23/go => github.com/cosmos/cosmos-sdk/ics23/go v0.8.0
-	github.com/cosmos/cosmos-sdk => github.com/sei-protocol/sei-cosmos v0.3.4
+	github.com/cosmos/cosmos-sdk => github.com/sei-protocol/sei-cosmos v0.3.5
 	github.com/cosmos/iavl => github.com/sei-protocol/sei-iavl v0.1.9
 	github.com/cosmos/ibc-go/v3 => github.com/sei-protocol/sei-ibc-go/v3 v3.3.0
 	github.com/ethereum/go-ethereum => github.com/sei-protocol/go-ethereum v1.13.5-sei-15
 	github.com/gogo/protobuf => github.com/regen-network/protobuf v1.3.3-alpha.regen.1
 	github.com/sei-protocol/sei-db => github.com/sei-protocol/sei-db v0.0.35
 	// Latest goleveldb is broken, we have to stick to this version
 	github.com/syndtr/goleveldb => github.com/syndtr/goleveldb v1.0.1-0.20210819022825-2ae1ddf74ef7
-	github.com/tendermint/tendermint => github.com/sei-protocol/sei-tendermint v0.3.0
+	github.com/tendermint/tendermint => github.com/sei-protocol/sei-tendermint v0.3.1
 	github.com/tendermint/tm-db => github.com/sei-protocol/tm-db v0.0.4
 	google.golang.org/grpc => google.golang.org/grpc v1.33.2
 )
```

### go.sum
```diff
@@ -1347,16 +1347,16 @@ github.com/sei-protocol/go-ethereum v1.13.5-sei-15 h1:VSFQrbWnSDCPCQzsYDW3k07EP3
 github.com/sei-protocol/go-ethereum v1.13.5-sei-15/go.mod h1:kcRZmuzRn1lVejiFNTz4l4W7imnpq1bDAnuKS/RyhbQ=
 github.com/sei-protocol/goutils v0.0.2 h1:Bfa7Sv+4CVLNM20QcpvGb81B8C5HkQC/kW1CQpIbXDA=
 github.com/sei-protocol/goutils v0.0.2/go.mod h1:iYE2DuJfEnM+APPehr2gOUXfuLuPsVxorcDO+Tzq9q8=
-github.com/sei-protocol/sei-cosmos v0.3.4 h1:bWgG/+J6xZmnEq74tjKzk1v9Rou0+m9o6fRS6Vkqpns=
-github.com/sei-protocol/sei-cosmos v0.3.4/go.mod h1:y86cNKDsiwsbhSoZZVCqGLUY8t6q9sUZl58kpaspI4Q=
+github.com/sei-protocol/sei-cosmos v0.3.5 h1:ibWj4uM3YeKLaGKfl1oWj36nkJo/2aZSyS7xo8Ixh6E=
+github.com/sei-protocol/sei-cosmos v0.3.5/go.mod h1:imKzUdlLFKj8H39Ej9dICT+HZkx0rgEPsVm0PPb59kc=
 github.com/sei-protocol/sei-db v0.0.35 h1:BNHv0gtKE4J5kq1Mhxt9dpop3lI4W2I5WurgWYIYa4E=
 github.com/sei-protocol/sei-db v0.0.35/go.mod h1:F/ZKZA8HJPcUzSZPA8yt6pfwlGriJ4RDR4eHKSGLStI=
 github.com/sei-protocol/sei-iavl v0.1.9 h1:y4mVYftxLNRs6533zl7N0/Ch+CzRQc04JDfHolIxgBE=
 github.com/sei-protocol/sei-iavl v0.1.9/go.mod h1:7PfkEVT5dcoQE+s/9KWdoXJ8VVVP1QpYYPLdxlkSXFk=
 github.com/sei-protocol/sei-ibc-go/v3 v3.3.0 h1:/mjpTuCSEVDJ51nUDSHU92N0bRSwt49r1rmdC/lqgp8=
 github.com/sei-protocol/sei-ibc-go/v3 v3.3.0/go.mod h1:VwB/vWu4ysT5DN2aF78d17LYmx3omSAdq6gpKvM7XRA=
-github.com/sei-protocol/sei-tendermint v0.3.0 h1:tzxuZeYgXy2wPhYXaX9vrc3dmzGE4oTWfxaCs5YJ3GA=
-github.com/sei-protocol/sei-tendermint v0.3.0/go.mod h1:4LSlJdhl3nf3OmohliwRNUFLOB1XWlrmSodrIP7fLh4=
+github.com/sei-protocol/sei-tendermint v0.3.1 h1:CzlJqFCFBoh0qlzUNc4n3HVNGD9FX+bGTKOyHkgMd4U=
+github.com/sei-protocol/sei-tendermint v0.3.1/go.mod h1:4LSlJdhl3nf3OmohliwRNUFLOB1XWlrmSodrIP7fLh4=
 github.com/sei-protocol/sei-tm-db v0.0.5 h1:3WONKdSXEqdZZeLuWYfK5hP37TJpfaUa13vAyAlvaQY=
 github.com/sei-protocol/sei-tm-db v0.0.5/go.mod h1:Cpa6rGyczgthq7/0pI31jys2Fw0Nfrc+/jKdP1prVqY=
 github.com/sei-protocol/sei-wasmd v0.1.2 h1:CHAQGWq0htMsJVo+4CWqz1uCCAMg6bTm1OUlD1mRZ5o=
```
