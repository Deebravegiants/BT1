# [?] fix: prevent race condition on L1Block address (#409)

## Summary
Severity: Unknown
Chain: Kroma
Component: kroma-network/kroma
Published: 2024-12-19
Source: https://github.com/kroma-network/kroma/commit/e07230ffdf121c322e64e134f94dc1a1221d8fd6
Type: security-commit

## Details
fix: prevent race condition on L1Block address (#409)

* fix: prevent race condition on L1Block address

* chore: bump geth version

* chore: remove devops from codeowners

---------

Co-authored-by: seolaoh <osa8361@gmail.com>

## Patch
### .github/CODEOWNERS
```diff
@@ -1,8 +1,3 @@
 # All
 
 * @kroma-network/l2-protocol
-
-# Ops
-
-/.github    @kroma-network/devops
-/ops-devnet @kroma-network/devops
```

### go.mod
```diff
@@ -207,4 +207,4 @@ require (
 
 replace github.com/ethereum-optimism/optimism v1.7.2 => ./
 
-replace github.com/ethereum/go-ethereum v1.13.8 => github.com/kroma-network/go-ethereum v1.101308.3-0.20241212085106-1e691c4eb53c
+replace github.com/ethereum/go-ethereum v1.13.8 => github.com/kroma-network/go-ethereum v1.101308.3-0.20241217074530-d90b21ebdd5d
```

### go.sum
```diff
@@ -395,8 +395,8 @@ github.com/kr/pty v1.1.3/go.mod h1:pFQYn66WHrOpPYNljwOMqo10TkYh1fy3cYio2l3bCsQ=
 github.com/kr/text v0.1.0/go.mod h1:4Jbv+DJW3UT/LiOwJeYQe1efqtUx/iVham/4vfdArNI=
 github.com/kr/text v0.2.0 h1:5Nx0Ya0ZqY2ygV366QzturHI13Jq95ApcVaJBhpS+AY=
 github.com/kr/text v0.2.0/go.mod h1:eLer722TekiGuMkidMxC/pM04lWEeraHUUmBw8l2grE=
-github.com/kroma-network/go-ethereum v1.101308.3-0.20241212085106-1e691c4eb53c h1:hZ9QJhCKF2HnAP8060XIXvjQM2JsDGPLOfTa+h901AI=
-github.com/kroma-network/go-ethereum v1.101308.3-0.20241212085106-1e691c4eb53c/go.mod h1:ZG4M8oph2j0C+R6CtUXuHeeUk5TuN5hVyl9gfwZawJg=
+github.com/kroma-network/go-ethereum v1.101308.3-0.20241217074530-d90b21ebdd5d h1:JQ8ZDikWrz3/AXvQSoNg+t4r9fj1SV+yDPylx5yevJg=
+github.com/kroma-network/go-ethereum v1.101308.3-0.20241217074530-d90b21ebdd5d/go.mod h1:ZG4M8oph2j0C+R6CtUXuHeeUk5TuN5hVyl9gfwZawJg=
 github.com/kroma-network/zktrie v0.5.1-0.20230420142222-950ce7a8ce84 h1:VpLCQx+tFV6Nk0hbs3Noyxma/q9wIDdyacKpGQWUMI8=
 github.com/kroma-network/zktrie v0.5.1-0.20230420142222-950ce7a8ce84/go.mod h1:w54LrYo5rJEV503BgMPRNONsLTOEQv5V87q+uYaw9sM=
 github.com/kylelemons/godebug v1.1.0 h1:RPNrshWIDI6G2gRW9EHilWtl7Z6Sb1BR0xunSBf0SNc=
```

### op-node/rollup/derive/l1_block_info.go
```diff
@@ -31,7 +31,6 @@ var (
 	L1InfoFuncBedrockBytes4 = crypto.Keccak256([]byte(L1InfoFuncBedrockSignature))[:4]
 	L1InfoFuncEcotoneBytes4 = crypto.Keccak256([]byte(L1InfoFuncEcotoneSignature))[:4]
 	L1InfoDepositerAddress  = common.HexToAddress("0xdeaddeaddeaddeaddeaddeaddeaddeaddead0001")
-	L1BlockAddress          = predeploys.KromaL1BlockAddr
 )
 
 const (
@@ -433,10 +432,9 @@ func L1InfoDeposit(rollupCfg *rollup.Config, sysCfg eth.SystemConfig, seqNumber
 	}
 
 	// [Kroma: START]
+	l1BlockAddress := predeploys.KromaL1BlockAddr
 	if rollupCfg.IsKromaMPT(l2BlockTime) {
-		L1BlockAddress = oppredeploys.L1BlockAddr
-	} else {
-		L1BlockAddress = predeploys.KromaL1BlockAddr
+		l1BlockAddress = oppredeploys.L1BlockAddr
 	}
 	// [Kroma: END]
 
@@ -445,7 +443,7 @@ func L1InfoDeposit(rollupCfg *rollup.Config, sysCfg eth.SystemConfig, seqNumber
 	out := &types.DepositTx{
 		SourceHash:          source.SourceHash(),
 		From:                L1InfoDepositerAddress,
-		To:                  &L1BlockAddress,
+		To:                  &l1BlockAddress,
 		Mint:                nil,
 		Value:               big.NewInt(0),
 		Gas:                 150_000_000,
```

### ops-devnet/docker-compose.yml
```diff
@@ -108,7 +108,7 @@ services:
 
   l2:
     pid: host # allow debugging
-    image: kromanetwork/geth:zkvm-1e691c4e
+    image: kromanetwork/geth:zkvm-d90b21eb
     ports:
       - "9545:8545"
       - "9546:8546"
@@ -128,7 +128,7 @@ services:
 
   l2-historical:
     pid: host # allow debugging
-    image: kromanetwork/geth:zkvm-1e691c4e
+    image: kromanetwork/geth:zkvm-d90b21eb
     ports:
       - "9445:8545"
       - "9446:8546"
```
