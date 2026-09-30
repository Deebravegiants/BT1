# [?] Fix testing bug : avoid datarace on a node crash during e2e test (#2031)

## Summary
Severity: Unknown
Chain: Algorand
Component: algorand/go-algorand
Published: 2021-04-01
Source: https://github.com/algorand/go-algorand/commit/920c6ee62440341320aebd2f75d0d0919230f2a0
Type: security-commit

## Details
Fix testing bug : avoid datarace on a node crash during e2e test (#2031)

## Overview
Synchronize `testing.T` access across go-routines to avoid generating a data race in case of an asynchronous node crash feedback.

## Summary
When the node controller notice that the node exits, it reports it back to the test fixture.
However, the test fixture cannot report that to the underlying test since doing so would create a data race : the `testing.T` is not meant to support concurrency.

To address that, this PR provides an abstraction over the `testing.T` called `TestingTB`, which retain the same functionality, but uses a mutex to synchronize the access.

## Patch
### test/e2e-go/cli/algod/cleanup_test.go
```diff
@@ -28,7 +28,7 @@ import (
 
 func TestNodeControllerCleanup(t *testing.T) {
 	t.Parallel()
-	a := require.New(t)
+	a := require.New(fixtures.SynchronizedTest(t))
 
 	var fixture fixtures.RestClientFixture
 	fixture.Setup(t, filepath.Join("nettemplates", "TwoNodesPartialPartkeyOnlyWallets.json"))
```

### test/e2e-go/cli/algod/stdstreams_test.go
```diff
@@ -44,7 +44,7 @@ func TestAlgodLogsToFile(t *testing.T) {
 }
 
 func testNodeCreatesLogFiles(t *testing.T, nc nodecontrol.NodeController, redirect bool) {
-	a := require.New(t)
+	a := require.New(fixtures.SynchronizedTest(t))
 
 	stdOutFile := filepath.Join(nc.GetDataDir(), nodecontrol.StdOutFilename)
 	exists := util.FileExists(stdOutFile)
```

### test/e2e-go/cli/goal/account_test.go
```diff
@@ -29,7 +29,7 @@ const statusOnline = "[online]"
 
 func TestAccountNew(t *testing.T) {
 	defer fixture.SetTestContext(t)()
-	a := require.New(t)
+	a := require.New(fixtures.SynchronizedTest(t))
 
 	newAcctName := "new_account"
 
@@ -54,7 +54,7 @@ func TestAccountNew(t *testing.T) {
 
 func TestAccountNewDuplicateFails(t *testing.T) {
 	defer fixture.SetTestContext(t)()
-	a := require.New(t)
+	a := require.New(fixtures.SynchronizedTest(t))
 
 	newAcctName := "duplicate_account"
 
@@ -69,7 +69,7 @@ func TestAccountNewDuplicateFails(t *testing.T) {
 
 func TestAccountRename(t *testing.T) {
 	defer fixture.SetTestContext(t)()
-	a := require.New(t)
+	a := require.New(fixtures.SynchronizedTest(t))
 
 	initialAcctName := "initial"
 	newAcctName := "renamed"
@@ -99,7 +99,7 @@ func TestAccountRename(t *testing.T) {
 // Importing an account multiple times should not be considered an error by goal
 func TestAccountMultipleImportRootKey(t *testing.T) {
 	defer fixture.SetTestContext(t)()
-	a := require.New(t)
+	a := require.New(fixtures.SynchronizedTest(t))
 
 	walletName := ""
 	createUnencryptedWallet := false
```

### test/e2e-go/cli/goal/clerk_test.go
```diff
@@ -22,11 +22,13 @@ import (
 	"time"
 
 	"github.com/stretchr/testify/require"
+
+	"github.com/algorand/go-algorand/test/framework/fixtures"
 )
 
 func TestClerkSendNoteEncoding(t *testing.T) {
 	defer fixture.SetTestContext(t)()
-	a := require.New(t)
+	a := require.New(fixtures.SynchronizedTest(t))
 
 	// wait for consensus on first round prior to sending transactions, time out after 2 minutes
 	err := fixture.WaitForRound(2, time.Duration(2*time.Minute))
```

### test/e2e-go/cli/goal/node_cleanup_test.go
```diff
@@ -22,11 +22,12 @@ import (
 	"github.com/stretchr/testify/require"
 
 	"github.com/algorand/go-algorand/nodecontrol"
+	"github.com/algorand/go-algorand/test/framework/fixtures"
 )
 
 func TestGoalNodeCleanup(t *testing.T) {
 	defer fixture.SetTestContext(t)()
-	a := require.New(t)
+	a := require.New(fixtures.SynchronizedTest(t))
 
 	primaryDir := fixture.PrimaryDataDir()
 	nc := nodecontrol.MakeNodeController(fixture.GetBinDir(), primaryDir)
```

### test/e2e-go/cli/perf/libgoal_test.go
```diff
@@ -34,19 +34,20 @@ func BenchmarkLibGoalPerf(b *testing.B) {
 	binDir := fixture.GetBinDir()
 
 	c, err := libgoal.MakeClientWithBinDir(binDir, fixture.PrimaryDataDir(), fixture.PrimaryDataDir(), libgoal.FullClient)
-	require.NoError(b, err)
+	a := require.New(fixtures.SynchronizedTest(b))
+	a.NoError(err)
 
 	b.Run("algod", func(b *testing.B) {
 		for i := 0; i < b.N; i++ {
 			_, err := c.AlgodVersions()
-			require.NoError(b, err)
+			a.NoError(err)
 		}
 	})
 
 	b.Run("kmd", func(b *testing.B) {
 		for i := 0; i < b.N; i++ {
 			_, err := c.GetUnencryptedWalletHandle()
-			require.NoError(b, err)
+			a.NoError(err)
 		}
 	})
 }
```

### test/e2e-go/cli/perf/payment_test.go
```diff
@@ -35,21 +35,23 @@ func BenchmarkSendPayment(b *testing.B) {
 	defer fixture.Shutdown()
 	binDir := fixture.GetBinDir()
 
+	a := require.New(fixtures.SynchronizedTest(b))
+
 	c, err := libgoal.MakeClientWithBinDir(binDir, fixture.PrimaryDataDir(), fixture.PrimaryDataDir(), libgoal.FullClient)
-	require.NoError(b, err)
+	a.NoError(err)
 
 	wallet, err := c.GetUnencryptedWalletHandle()
-	require.NoError(b, err)
+	a.NoError(err)
 
 	addrs, err := c.ListAddresses(wallet)
-	require.NoError(b, err)
-	require.True(b, len(addrs) > 0)
+	a.NoError(err)
+	a.True(len(addrs) > 0)
 	addr := addrs[0]
 
 	b.Run("getwallet", func(b *testing.B) {
 		for i := 0; i < b.N; i++ {
 			_, err = c.GetUnencryptedWalletHandle()
-			require.NoError(b, err)
+			a.NoError(err)
 		}
 	})
 
@@ -59,14 +61,14 @@ func BenchmarkSendPayment(b *testing.B) {
 			var nonce [8]byte
 			crypto.RandBytes(nonce[:])
 			tx, err = c.ConstructPayment(addr, addr, 1, 1, nonce[:], "", [32]byte{}, 0, 0)
-			require.NoError(b, err)
+			a.NoError(err)
 		}
 	})
 
 	b.Run("signtxn", func(b *testing.B) {
 		for i := 0; i < b.N; i++ {
 			_, err = c.SignTransactionWithWallet(wallet, nil, tx)
-			require.NoError(b, err)
+			a.NoError(err)
 		}
 	})
 
@@ -75,7 +77,7 @@ func BenchmarkSendPayment(b *testing.B) {
 			var nonce [8]byte
 			crypto.RandBytes(nonce[:])
 			_, err := c.SendPaymentFromWallet(wallet, nil, addr, addr, 1, 1, nonce[:], "", 0, 0)
-			require.NoError(b, err)
+			a.NoError(err)
 		}
 	})
 }
```

### test/e2e-go/features/auction/auctionCancel_test.go
```diff
@@ -31,7 +31,7 @@ func TestStartAndCancelAuctionNoBids(t *testing.T) {
 		t.Skip()
 	}
 	t.Parallel()
-	r := require.New(t)
+	r := require.New(fixtures.SynchronizedTest(t))
 	var fixture fixtures.AuctionFixture
 	netTemplate := filepath.Join("nettemplates", "ThreeNodesEvenDist.json")
 	auctionParamFile := filepath.Join("auctions", "AuctionParams_1.json")
@@ -62,7 +62,7 @@ func TestStartAndCancelAuctionOneUserTenBids(t *testing.T) {
 		t.Skip()
 	}
 	t.Parallel()
-	r := require.New(t)
+	r := require.New(fixtures.SynchronizedTest(t))
 	var fixture fixtures.AuctionFixture
 	netTemplate := filepath.Join("nettemplates", "TwoNodes50Each.json")
 	auctionParamFile := filepath.Join("auctions", "AuctionParams_1.json")
@@ -122,7 +122,7 @@ func TestStartAndCancelAuctionOneUserTenBids(t *testing.T) {
 
 func TestStartAndCancelAuctionEarlyOneUserTenBids(t *testing.T) {
 	t.Parallel()
-	r := require.New(t)
+	r := require.New(fixtures.SynchronizedTest(t))
 	var fixture fixtures.AuctionFixture
 	netTemplate := filepath.Join("nettemplates", "TwoNodes50Each.json")
 	auctionParamFile := filepath.Join("auctions", "AuctionParams_1.json")
```

### test/e2e-go/features/auction/auctionErrors_test.go
```diff
@@ -35,7 +35,7 @@ func TestInvalidDeposit(t *testing.T) {
 		t.Skip()
 	}
 	t.Parallel()
-	r := require.New(t)
+	r := require.New(fixtures.SynchronizedTest(t))
 
 	var fixture fixtures.AuctionFixture
 	netTemplate := filepath.Join("nettemplates", "TwoNodes50Each.json")
@@ -123,7 +123,7 @@ func TestNoDepositAssociatedWithBid(t *testing.T) {
 		t.Skip()
 	}
 	t.Parallel()
-	r := require.New(t)
+	r := require.New(fixtures.SynchronizedTest(t))
 
 	var fixture fixtures.AuctionFixture
 	netTemplate := filepath.Join("nettemplates", "TwoNodes50Each.json")
@@ -192,7 +192,7 @@ func TestNoDepositAssociatedWithBid(t *testing.T) {
 func TestDeadbeatBid(t *testing.T) {
 	// an error is expected when an account attempts to overbid
 	t.Parallel()
-	r := require.New(t)
+	r := require.New(fixtures.SynchronizedTest(t))
 
 	var fixture fixtures.AuctionFixture
 	netTemplate := filepath.Join("nettemplates", "TwoNodes50Each.json")
@@ -290,7 +290,7 @@ func TestStartAndPartitionAuctionTenUsersTenBidsEach(t *testing.T) {
 		t.Skip()
 	}
 	t.Parallel()
-	r := require.New(t)
+	r := require.New(fixtures.SynchronizedTest(t))
 	var fixture fixtures.AuctionFixture
 	netTemplate := filepath.Join("nettemplates", "TwoNodes50Each.json")
 	auctionParamFile := filepath.Join("auctions", "AuctionParams_1.json")
@@ -299,7 +299,7 @@ func TestStartAndPartitionAuctionTenUsersTenBidsEach(t *testing.T) {
 	libGoalClient := fixture.GetLibGoalClient()
 
 	minTxnFee, minAcctBalance, err := fixture.CurrentMinFeeAndBalance()
-	require.NoError(t, err)
+	r.NoError(err)
 
 	// create wallets to bid with, and note their balances before the auction.
 	wallets, _ := fixture.GetWalletsSortedByBalance()
```

### test/e2e-go/features/auction/basicAuction_test.go
```diff
@@ -43,7 +43,7 @@ func TestStartAndEndAuctionNoBids(t *testing.T) {
 		t.Skip()
 	}
 	t.Parallel()
-	r := require.New(t)
+	r := require.New(fixtures.SynchronizedTest(t))
 	var fixture fixtures.AuctionFixture
 	netTemplate := filepath.Join("nettemplates", "ThreeNodesEvenDist.json")
 	auctionParamFile := filepath.Join("auctions", "AuctionParams_1.json")
@@ -84,7 +84,7 @@ func TestStartAndEndAuctionOneUserOneBid(t *testing.T) {
 		t.Skip()
 	}
 	t.Parallel()
-	r := require.New(t)
+	r := require.New(fixtures.SynchronizedTest(t))
 	var fixture fixtures.AuctionFixture
 	netTemplate := filepath.Join("nettemplates", "TwoNodes50Each.json")
 	auctionParamFile := filepath.Join("auctions", "AuctionParams_1.json")
@@ -153,7 +153,7 @@ func TestStartAndEndAuctionOneUserTenBids(t *testing.T) {
 		t.Skip()
 	}
 	t.Parallel()
-	r := require.New(t)
+	r := require.New(fixtures.SynchronizedTest(t))
 	var fixture fixtures.AuctionFixture
 	netTemplate := filepath.Join("nettemplates", "TwoNodes50Each.json")
 	auctionParamFile := filepath.Join("auctions", "AuctionParams_1.json")
@@ -222,7 +222,7 @@ func TestStartAndEndAuctionOneUserTenBids(t *testing.T) {
 
 func TestStartAndEndAuctionTenUsersOneBidEach(t *testing.T) {
 	t.Parallel()
-	r := require.New(t)
+	r := require.New(fixtures.SynchronizedTest(t))
 	var fixture fixtures.AuctionFixture
 	netTemplate := filepath.Join("nettemplates", "TwoNodes50Each.json")
 	auctionParamFile := filepath.Join("auctions", "AuctionParams_1.json")
@@ -317,7 +317,7 @@ func TestStartAndEndAuctionTenUsersTenBidsEach(t *testing.T) {
 		t.Skip()
 	}
 	t.Parallel()
-	r := require.New(t)
+	r := require.New(fixtures.SynchronizedTest(t))
 	var fixture fixtures.AuctionFixture
 	netTemplate := filepath.Join("nettemplates", "TwoNodes50Each.json")
 	auctionParamFile := filepath.Join("auctions", "AuctionParams_1.json")
@@ -326,7 +326,7 @@ func TestStartAndEndAuctionTenUsersTenBidsEach(t *testing.T) {
 	libGoalClient := fixture.GetLibGoalClient()
 
 	minTxnFee, minAcctBalance, err := fixture.CurrentMinFeeAndBalance()
-	require.NoError(t, err)
+	r.NoError(err)
 
 	// create wallets to bid with, and note their balances before the auction.
 	wallets, _ := fixture.GetWalletsSortedByBalance()
@@ -414,7 +414,7 @@ func TestDecayingPrice(t *testing.T) {
 		t.Skip()
 	}
 	t.Parallel()
-	r := require.New(t)
+	r := require.New(fixtures.SynchronizedTest(t))
 	var fixture fixtures.AuctionFixture
 	netTemplate := filepath.Join("nettemplates", "TwoNodes50Each.json")
 	// "price goes from 10 to 1, decreasing by 1 each block for 10 blocks."
```

### test/e2e-go/features/catchup/basicCatchup_test.go
```diff
@@ -35,7 +35,7 @@ func TestBasicCatchup(t *testing.T) {
 		t.Skip()
 	}
 	t.Parallel()
-	a := require.New(t)
+	a := require.New(fixtures.SynchronizedTest(t))
 
 	// Overview of this test:
 	// Start a two-node network (primary has 0%, secondary has 100%)
@@ -78,21 +78,22 @@ func TestBasicCatchup(t *testing.T) {
 func TestCatchupOverGossip(t *testing.T) {
 	t.Parallel()
 
+	syncTest := fixtures.SynchronizedTest(t)
 	supportedVersions := network.SupportedProtocolVersions
-	require.LessOrEqual(t, len(supportedVersions), 3)
+	require.LessOrEqual(syncTest, len(supportedVersions), 3)
 
 	// ledger node upgraded version, fetcher node upgraded version
 	// Run with the default values. Instead of "", pass the default value
 	// to exercise loading it from the config file.
-	runCatchupOverGossip(t, supportedVersions[0], supportedVersions[0])
+	runCatchupOverGossip(syncTest, supportedVersions[0], supportedVersions[0])
 	for i := 1; i < len(supportedVersions); i++ {
 		runCatchupOverGossip(t, supportedVersions[i], "")
 		runCatchupOverGossip(t, "", supportedVersions[i])
 		runCatchupOverGossip(t, supportedVersions[i], supportedVersions[i])
 	}
 }
 
-func runCatchupOverGossip(t *testing.T,
+func runCatchupOverGossip(t fixtures.TestingTB,
 	ledgerNodeDowngradeTo,
 	fetcherNodeDowngradeTo string) {
 
@@ -117,7 +118,7 @@ func runCatchupOverGossip(t *testing.T,
 		a.NoError(err)
 		cfg, err := config.LoadConfigFromDisk(dir)
 		a.NoError(err)
-		require.Empty(t, cfg.NetworkProtocolVersion)
+		a.Empty(cfg.NetworkProtocolVersion)
 		cfg.NetworkProtocolVersion = ledgerNodeDowngradeTo
 		cfg.SaveToDisk(dir)
 	}
@@ -127,7 +128,7 @@ func runCatchupOverGossip(t *testing.T,
 		dir := fixture.PrimaryDataDir()
 		cfg, err := config.LoadConfigFromDisk(dir)
 		a.NoError(err)
-		require.Empty(t, cfg.NetworkProtocolVersion)
+		a.Empty(cfg.NetworkProtocolVersion)
 		cfg.NetworkProtocolVersion = fetcherNodeDowngradeTo
 		cfg.SaveToDisk(dir)
 	}
@@ -177,7 +178,7 @@ func runCatchupOverGossip(t *testing.T,
 
 		if time.Now().Sub(waitStart) > time.Minute {
 			// it's taking too long.
-			require.FailNow(t, "Waiting too long for catchup to complete")
+			a.FailNow("Waiting too long for catchup to complete")
 		}
 
 		time.Sleep(50 * time.Millisecond)
@@ -198,7 +199,7 @@ func TestStoppedCatchupOnUnsupported(t *testing.T) {
 		t.Skip()
 	}
 	t.Parallel()
-	a := require.New(t)
+	a := require.New(fixtures.SynchronizedTest(t))
 
 	consensus := make(config.ConsensusProtocols)
 	// The following two protocols: testUnupgradedProtocol and testUnupgradedToProtocol
```

### test/e2e-go/features/catchup/catchpointCatchup_test.go
```diff
@@ -41,7 +41,7 @@ type nodeExitErrorCollector struct {
 	errors   []error
 	messages []string
 	mu       deadlock.Mutex
-	t        *testing.T
+	t        fixtures.TestingTB
 }
 
 func (ec *nodeExitErrorCollector) nodeExitWithError(nc *nodecontrol.NodeController, err error) {
@@ -82,7 +82,7 @@ func TestBasicCatchpointCatchup(t *testing.T) {
 	if testing.Short() {
 		t.Skip()
 	}
-	a := require.New(t)
+	a := require.New(fixtures.SynchronizedTest(t))
 	log := logging.TestingLog(t)
 
 	// Overview of this test:
@@ -115,7 +115,7 @@ func TestBasicCatchpointCatchup(t *testing.T) {
 	var fixture fixtures.RestClientFixture
 	fixture.SetConsensus(consensus)
 
-	errorsCollector := nodeExitErrorCollector{t: t}
+	errorsCollector := nodeExitErrorCollector{t: fixtures.SynchronizedTest(t)}
 	defer errorsCollector.Print()
 
 	// Give the second node (which starts up last) all the stake so that its proposal always has better credentials,
```
