# [?] fix: Disable CI/CD linter check with rand library, fix server overlap, and data race issue (#916)

## Summary
Severity: Unknown
Chain: Rollkit
Component: evstack/ev-node
Published: 2023-05-05
Source: https://github.com/evstack/ev-node/commit/d7f67729b8efeeaeeeb81c5ad4c6bd4a42435955
Type: security-commit

## Details
fix: Disable CI/CD linter check with rand library, fix server overlap, and data race issue (#916)

Resolves #911, resolves #919, resolves #910

## Patch
### da/test/da_test.go
```diff
@@ -3,6 +3,7 @@ package test
 import (
 	"context"
 	"encoding/json"
+	"fmt"
 	"math/rand"
 	"net"
 	"os"
@@ -32,10 +33,27 @@ const mockDaBlockTime = 100 * time.Millisecond
 
 var testNamespaceID = types.NamespaceID{0, 1, 2, 3, 4, 5, 6, 7}
 
-func TestLifecycle(t *testing.T) {
-	srv := startMockGRPCServ(t)
-	defer srv.GracefulStop()
+func TestMain(m *testing.M) {
+	srv := startMockGRPCServ()
+	if srv == nil {
+		os.Exit(1)
+	}
+
+	httpServer := startMockCelestiaNodeServer()
+	if httpServer == nil {
+		os.Exit(1)
+	}
 
+	exitCode := m.Run()
+
+	// teardown servers
+	srv.GracefulStop()
+	httpServer.Stop()
+
+	os.Exit(exitCode)
+}
+
+func TestLifecycle(t *testing.T) {
 	for _, dalc := range registry.RegisteredClients() {
 		t.Run(dalc, func(t *testing.T) {
 			doTestLifecycle(t, registry.GetClient(dalc))
@@ -57,12 +75,6 @@ func doTestLifecycle(t *testing.T, dalc da.DataAvailabilityLayerClient) {
 }
 
 func TestDALC(t *testing.T) {
-	grpcServer := startMockGRPCServ(t)
-	defer grpcServer.GracefulStop()
-
-	httpServer := startMockCelestiaNodeServer(t)
-	defer httpServer.Stop()
-
 	for _, dalc := range registry.RegisteredClients() {
 		t.Run(dalc, func(t *testing.T) {
 			doTestDALC(t, registry.GetClient(dalc))
@@ -128,12 +140,6 @@ func doTestDALC(t *testing.T, dalc da.DataAvailabilityLayerClient) {
 }
 
 func TestRetrieve(t *testing.T) {
-	grpcServer := startMockGRPCServ(t)
-	defer grpcServer.GracefulStop()
-
-	httpServer := startMockCelestiaNodeServer(t)
-	defer httpServer.Stop()
-
 	for _, client := range registry.RegisteredClients() {
 		t.Run(client, func(t *testing.T) {
 			dalc := registry.GetClient(client)
@@ -145,33 +151,34 @@ func TestRetrieve(t *testing.T) {
 	}
 }
 
-func startMockGRPCServ(t *testing.T) *grpc.Server {
-	t.Helper()
+func startMockGRPCServ() *grpc.Server {
 	conf := grpcda.DefaultConfig
 	logger := tmlog.NewTMLogger(os.Stdout)
 
 	kvStore, _ := store.NewDefaultInMemoryKVStore()
 	srv := mockserv.GetServer(kvStore, conf, []byte(mockDaBlockTime.String()), logger)
 	lis, err := net.Listen("tcp", conf.Host+":"+strconv.Itoa(conf.Port))
 	if err != nil {
-		t.Fatal(err)
+		fmt.Println(err)
+		return nil
 	}
 	go func() {
 		_ = srv.Serve(lis)
 	}()
 	return srv
 }
 
-func startMockCelestiaNodeServer(t *testing.T) *cmock.Server {
-	t.Helper()
-	httpSrv := cmock.NewServer(mockDaBlockTime, test.NewLogger(t))
+func startMockCelestiaNodeServer() *cmock.Server {
+	httpSrv := cmock.NewServer(mockDaBlockTime, tmlog.NewTMLogger(os.Stdout))
 	l, err := net.Listen("tcp4", "127.0.0.1:26658")
 	if err != nil {
-		t.Fatal("failed to create listener for mock celestia-node RPC server", "error", err)
+		fmt.Println("failed to create listener for mock celestia-node RPC server, error: %w", err)
+		return nil
 	}
 	err = httpSrv.Start(l)
 	if err != nil {
-		t.Fatal("can't start mock celestia-node RPC server")
+		fmt.Println("can't start mock celestia-node RPC server")
+		return nil
 	}
 	return httpSrv
 }
```

### libs/testfactory/txs.go
```diff
@@ -9,7 +9,7 @@ import (
 func GenerateRandomlySizedTxs(count, maxSize int) types.Txs {
 	txs := make(types.Txs, count)
 	for i := 0; i < count; i++ {
-		size := mrand.Intn(maxSize)
+		size := mrand.Intn(maxSize) //nolint:gosec
 		if size == 0 {
 			size = 1
 		}
@@ -22,7 +22,7 @@ func GenerateRandomTxs(count, size int) types.Txs {
 	txs := make(types.Txs, count)
 	for i := 0; i < count; i++ {
 		tx := make([]byte, size)
-		_, err := mrand.Read(tx)
+		_, err := mrand.Read(tx) //nolint:gosec
 		if err != nil {
 			panic(err)
 		}
```

### p2p/client.go
```diff
@@ -10,6 +10,7 @@ import (
 	"github.com/libp2p/go-libp2p"
 	dht "github.com/libp2p/go-libp2p-kad-dht"
 	pubsub "github.com/libp2p/go-libp2p-pubsub"
+
 	"github.com/libp2p/go-libp2p/core/crypto"
 	cdiscovery "github.com/libp2p/go-libp2p/core/discovery"
 	"github.com/libp2p/go-libp2p/core/host"
```

### p2p/gossip.go
```diff
@@ -92,9 +92,14 @@ func (g *Gossiper) Publish(ctx context.Context, data []byte) error {
 func (g *Gossiper) ProcessMessages(ctx context.Context) {
 	for {
 		_, err := g.sub.Next(ctx)
-		if err != nil {
-			g.logger.Error("failed to read message", "error", err)
+		select {
+		case <-ctx.Done():
 			return
+		default:
+			if err != nil {
+				g.logger.Error("failed to read message", "error", err)
+				return
+			}
 		}
 		// Logic is handled in validator
 	}
```
