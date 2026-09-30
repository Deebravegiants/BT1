# [?] Fix panic on nil block in ethstats (#1360)

## Summary
Severity: Unknown
Chain: Polygon
Component: 0xPolygon/bor
Published: 2024-10-25
Source: https://github.com/0xPolygon/bor/commit/698f22fd183679576abafd81d5c0cb0e8019b38f
Type: security-commit

## Details
Fix panic on nil block in ethstats (#1360)

## Patch
### ethstats/ethstats.go
```diff
@@ -729,6 +729,10 @@ func (s *Service) assembleBlockStats(block *types.Block) *blockStats {
 			}
 		}
 
+		if block == nil {
+			return nil
+		}
+
 		header = block.Header()
 		td = fullBackend.GetTd(context.Background(), header.Hash())
 
```

### ethstats/ethstats_test.go
```diff
@@ -17,8 +17,17 @@
 package ethstats
 
 import (
+	"context"
+	"math/big"
 	"strconv"
 	"testing"
+
+	"github.com/ethereum/go-ethereum"
+	"github.com/ethereum/go-ethereum/common"
+	"github.com/ethereum/go-ethereum/core"
+	"github.com/ethereum/go-ethereum/core/types"
+	"github.com/ethereum/go-ethereum/event"
+	"github.com/ethereum/go-ethereum/rpc"
 )
 
 func TestParseEthstatsURL(t *testing.T) {
@@ -83,3 +92,63 @@ func TestParseEthstatsURL(t *testing.T) {
 		}
 	}
 }
+
+// MockBackend is a mock implementation of the backend interface
+type MockFullNodeBackend struct{}
+
+func (m *MockFullNodeBackend) SubscribeChainHeadEvent(ch chan<- core.ChainHeadEvent) event.Subscription {
+	return nil
+}
+
+func (m *MockFullNodeBackend) SubscribeNewTxsEvent(ch chan<- core.NewTxsEvent) event.Subscription {
+	return nil
+}
+
+func (m *MockFullNodeBackend) CurrentHeader() *types.Header {
+	return &types.Header{}
+}
+
+func (m *MockFullNodeBackend) HeaderByNumber(ctx context.Context, number rpc.BlockNumber) (*types.Header, error) {
+	return nil, nil
+}
+
+func (m *MockFullNodeBackend) GetTd(ctx context.Context, hash common.Hash) *big.Int {
+	return big.NewInt(0)
+}
+
+func (m *MockFullNodeBackend) Stats() (pending int, queued int) {
+	return 0, 0
+}
+
+func (m *MockFullNodeBackend) SyncProgress() ethereum.SyncProgress {
+	return ethereum.SyncProgress{}
+}
+
+func (m *MockFullNodeBackend) SubscribeChain2HeadEvent(ch chan<- core.Chain2HeadEvent) event.Subscription {
+	return nil
+}
+
+func (m *MockFullNodeBackend) BlockByNumber(ctx context.Context, number rpc.BlockNumber) (*types.Block, error) {
+	return nil, nil
+}
+
+func (m *MockFullNodeBackend) CurrentBlock() *types.Header {
+	return &types.Header{Number: big.NewInt(1)}
+}
+
+func (m *MockFullNodeBackend) SuggestGasTipCap(ctx context.Context) (*big.Int, error) {
+	return big.NewInt(0), nil
+}
+
+func TestAssembleBlockStats_NilBlock(t *testing.T) {
+	mockBackend := &MockFullNodeBackend{}
+	service := &Service{
+		backend: mockBackend,
+	}
+
+	result := service.assembleBlockStats(nil)
+
+	if result != nil {
+		t.Errorf("Expected nil, got %v", result)
+	}
+}
```
