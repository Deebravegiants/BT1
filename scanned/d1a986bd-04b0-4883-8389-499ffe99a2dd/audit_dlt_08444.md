# [?] Switch to tm-db & sdk verison that fixes introduced deadlock

## Summary
Severity: Unknown
Chain: Osmosis
Component: osmosis-labs/osmosis
Published: 2021-09-11
Source: https://github.com/osmosis-labs/osmosis/commit/43f98c4106bfb9b738a758e1504a932b14b4a96b
Type: security-commit

## Details
Switch to tm-db & sdk verison that fixes introduced deadlock

## Patch
### go.mod
```diff
@@ -31,4 +31,6 @@ replace google.golang.org/grpc => google.golang.org/grpc v1.33.2
 
 replace github.com/gogo/protobuf => github.com/regen-network/protobuf v1.3.2-alpha.regen.4
 
-replace github.com/cosmos/cosmos-sdk => github.com/osmosis-labs/cosmos-sdk v0.42.10-0.20210829064313-2c87644925da
+replace github.com/cosmos/cosmos-sdk => github.com/osmosis-labs/cosmos-sdk v0.42.10-0.20210911034651-29525c35cdb8
+
+replace github.com/tendermint/tm-db => github.com/osmosis-labs/tm-db v0.6.5-0.20210911033928-ba9154613417
```

### go.sum
```diff
@@ -404,6 +404,10 @@ github.com/osmosis-labs/cosmos-sdk v0.42.10-0.20210829035621-cec66b14cc50 h1:Mh2
 github.com/osmosis-labs/cosmos-sdk v0.42.10-0.20210829035621-cec66b14cc50/go.mod h1:SrclJP9lMXxz2fCbngxb0brsPNuZXqoQQ9VHuQ3Tpf4=
 github.com/osmosis-labs/cosmos-sdk v0.42.10-0.20210829064313-2c87644925da h1:kg60BcOfzv5k/2xJuLhpqPzx+/mQ2KRceRIPSvnduxk=
 github.com/osmosis-labs/cosmos-sdk v0.42.10-0.20210829064313-2c87644925da/go.mod h1:SrclJP9lMXxz2fCbngxb0brsPNuZXqoQQ9VHuQ3Tpf4=
+github.com/osmosis-labs/cosmos-sdk v0.42.10-0.20210911034651-29525c35cdb8 h1:pL3NS/lk8ejBhu1pDLAolTNEQUammpCNa9Kt7jwhmcc=
+github.com/osmosis-labs/cosmos-sdk v0.42.10-0.20210911034651-29525c35cdb8/go.mod h1:QByRyM6mubdL7o30ZuJTFWT2cwjmT+GT19XSYwyS7pc=
+github.com/osmosis-labs/tm-db v0.6.5-0.20210911033928-ba9154613417 h1:otchJDd2SjFWfs7Tse3ULblGcVWqMJ50BE02XCaqXOo=
+github.com/osmosis-labs/tm-db v0.6.5-0.20210911033928-ba9154613417/go.mod h1:dptYhIpJ2M5kUuenLr+Yyf3zQOv1SgBZcl8/BmWlMBw=
 github.com/otiai10/copy v1.6.0 h1:IinKAryFFuPONZ7cm6T6E2QX/vcJwSnlaA5lfoaXIiQ=
 github.com/otiai10/copy v1.6.0/go.mod h1:XWfuS3CrI0R6IE0FbgHsEazaXO8G0LpMp9o8tos0x4E=
 github.com/otiai10/curr v0.0.0-20150429015615-9b4961190c95/go.mod h1:9qAhocn7zKJG+0mI8eUu6xqkFDYS2kb2saOteoSB3cE=
```

### x/lockup/keeper/lock_test.go
```diff
@@ -247,13 +247,17 @@ func (suite *KeeperTestSuite) TestLockTokensAlot() {
 	addr1 := sdk.AccAddress([]byte("addr1---------------"))
 	coins := sdk.Coins{sdk.NewInt64Coin("stake", 10)}
 	startAveragingAt := 1000
-	totalNumLocks := 5000
+	totalNumLocks := 10000
 	for i := 1; i < startAveragingAt; i++ {
 		suite.LockTokens(addr1, coins, time.Second)
 	}
 	runningTotal := uint64(0)
 	maxGas := uint64(0)
 	for i := startAveragingAt; i < totalNumLocks; i++ {
+		if i%1000 == 0 {
+			fmt.Printf("entering %dth lock now\n", i)
+		}
+
 		alreadySpent := suite.ctx.GasMeter().GasConsumed()
 		suite.LockTokens(addr1, coins, time.Second)
 		newSpent := suite.ctx.GasMeter().GasConsumed()
@@ -263,7 +267,7 @@ func (suite *KeeperTestSuite) TestLockTokensAlot() {
 			maxGas = spentNow
 		}
 	}
-	fmt.Println("test deets: total locks created %i, begin average at %i", totalNumLocks, startAveragingAt)
+	fmt.Printf("test deets: total locks created %d, begin average at %d\n", totalNumLocks, startAveragingAt)
 	fmt.Println("average gas / lock:", runningTotal/(uint64(totalNumLocks-startAveragingAt)))
 	fmt.Println("max gas / lock:", maxGas)
 
```
