# [?] fix: nil pointer dereference in RemoteABCIClientV1.FinalizeBlock (#6694)

## Summary
Severity: Unknown
Chain: Celestia
Component: celestiaorg/celestia-app
Published: 2026-03-03
Source: https://github.com/celestiaorg/celestia-app/commit/634034060cf032c17a875c0b6333e8ade060aaf3
Type: security-commit

## Details
fix: nil pointer dereference in RemoteABCIClientV1.FinalizeBlock (#6694)

## Summary

- Fix nil pointer dereference in `RemoteABCIClientV1.FinalizeBlock` when
`EndBlock` response has nil `ConsensusParamUpdates` or nil `Version`
(the common case for non-upgrade blocks)
- Add unit tests for `FinalizeBlock` covering nil
`ConsensusParamUpdates`, nil `Version`, and the happy path with a
version update

Closes #6540

## Test plan

- [x] `go test -v -run TestFinalizeBlock ./multiplexer/abci/` passes all
three subtests
- [x] `go test -v ./multiplexer/abci/` passes all existing tests

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-authored-by: Claude Opus 4.6 <noreply@anthropic.com>

## Patch
### multiplexer/abci/remote_v1.go
```diff
@@ -200,7 +200,9 @@ func (a *RemoteABCIClientV1) FinalizeBlock(req *abciv2.RequestFinalizeBlock) (*a
 	// set the retain height, used in commit noop
 	a.commitRetainLastHeight = commitResp.RetainHeight
 	// get the app version from the end block response
-	a.endBlockConsensusAppVersion = endBlockResp.GetConsensusParamUpdates().Version.AppVersion
+	if cp := endBlockResp.GetConsensusParamUpdates(); cp != nil && cp.GetVersion() != nil {
+		a.endBlockConsensusAppVersion = cp.GetVersion().AppVersion
+	}
 
 	return &abciv2.ResponseFinalizeBlock{
 		Events:                events,
```

### multiplexer/abci/remote_v1_test.go
```diff
@@ -5,12 +5,81 @@ import (
 	"testing"
 
 	abciv2 "github.com/cometbft/cometbft/abci/types"
+	typesv2 "github.com/cometbft/cometbft/proto/tendermint/types"
 	"github.com/stretchr/testify/assert"
 	"github.com/stretchr/testify/require"
 	abciv1 "github.com/tendermint/tendermint/abci/types"
+	typesv1 "github.com/tendermint/tendermint/proto/tendermint/types"
 	"google.golang.org/grpc"
 )
 
+func TestFinalizeBlock(t *testing.T) {
+	// minimalRequest returns a RequestFinalizeBlock with enough fields populated
+	// to avoid nil dereferences in the method under test.
+	minimalRequest := func() *abciv2.RequestFinalizeBlock {
+		return &abciv2.RequestFinalizeBlock{
+			Height: 1,
+			Header: &typesv2.Header{
+				LastBlockId: typesv2.BlockID{
+					PartSetHeader: typesv2.PartSetHeader{},
+				},
+			},
+		}
+	}
+
+	newMockClient := func(endBlockResp *abciv1.ResponseEndBlock) *mockABCIApplicationClient {
+		return &mockABCIApplicationClient{
+			infoResp:       &abciv1.ResponseInfo{AppVersion: 1},
+			beginBlockResp: &abciv1.ResponseBeginBlock{},
+			deliverTxResp:  &abciv1.ResponseDeliverTx{},
+			endBlockResp:   endBlockResp,
+			commitResp:     &abciv1.ResponseCommit{Data: []byte("apphash")},
+		}
+	}
+
+	t.Run("nil ConsensusParamUpdates should not panic", func(t *testing.T) {
+		mockClient := newMockClient(&abciv1.ResponseEndBlock{
+			ConsensusParamUpdates: nil,
+		})
+		client := &RemoteABCIClientV1{ABCIApplicationClient: mockClient}
+
+		resp, err := client.FinalizeBlock(minimalRequest())
+		require.NoError(t, err)
+		require.NotNil(t, resp)
+		assert.Equal(t, uint64(0), client.endBlockConsensusAppVersion)
+	})
+
+	t.Run("nil Version in ConsensusParamUpdates should not panic", func(t *testing.T) {
+		mockClient := newMockClient(&abciv1.ResponseEndBlock{
+			ConsensusParamUpdates: &abciv1.ConsensusParams{
+				Version: nil,
+			},
+		})
+		client := &RemoteABCIClientV1{ABCIApplicationClient: mockClient}
+
+		resp, err := client.FinalizeBlock(minimalRequest())
+		require.NoError(t, err)
+		require.NotNil(t, resp)
+		assert.Equal(t, uint64(0), client.endBlockConsensusAppVersion)
+	})
+
+	t.Run("ConsensusParamUpdates with Version sets app version", func(t *testing.T) {
+		mockClient := newMockClient(&abciv1.ResponseEndBlock{
+			ConsensusParamUpdates: &abciv1.ConsensusParams{
+				Version: &typesv1.VersionParams{
+					AppVersion: 42,
+				},
+			},
+		})
+		client := &RemoteABCIClientV1{ABCIApplicationClient: mockClient}
+
+		resp, err := client.FinalizeBlock(minimalRequest())
+		require.NoError(t, err)
+		require.NotNil(t, resp)
+		assert.Equal(t, uint64(42), client.endBlockConsensusAppVersion)
+	})
+}
+
 func TestConsensusParamsV1ToV2(t *testing.T) {
 	t.Run("should return nil if params are nil", func(t *testing.T) {
 		got := consensusParamsV1ToV2(nil)
@@ -61,9 +130,29 @@ func TestInfo(t *testing.T) {
 // mockABCIApplicationClient is a mock implementation of ABCIApplicationClient
 type mockABCIApplicationClient struct {
 	abciv1.ABCIApplicationClient
-	infoResp *abciv1.ResponseInfo
+	infoResp       *abciv1.ResponseInfo
+	beginBlockResp *abciv1.ResponseBeginBlock
+	deliverTxResp  *abciv1.ResponseDeliverTx
+	endBlockResp   *abciv1.ResponseEndBlock
+	commitResp     *abciv1.ResponseCommit
 }
 
-func (m *mockABCIApplicationClient) Info(ctx context.Context, req *abciv1.RequestInfo, opts ...grpc.CallOption) (*abciv1.ResponseInfo, error) {
+func (m *mockABCIApplicationClient) Info(_ context.Context, _ *abciv1.RequestInfo, _ ...grpc.CallOption) (*abciv1.ResponseInfo, error) {
 	return m.infoResp, nil
 }
+
+func (m *mockABCIApplicationClient) BeginBlock(_ context.Context, _ *abciv1.RequestBeginBlock, _ ...grpc.CallOption) (*abciv1.ResponseBeginBlock, error) {
+	return m.beginBlockResp, nil
+}
+
+func (m *mockABCIApplicationClient) DeliverTx(_ context.Context, _ *abciv1.RequestDeliverTx, _ ...grpc.CallOption) (*abciv1.ResponseDeliverTx, error) {
+	return m.deliverTxResp, nil
+}
+
+func (m *mockABCIApplicationClient) EndBlock(_ context.Context, _ *abciv1.RequestEndBlock, _ ...grpc.CallOption) (*abciv1.ResponseEndBlock, error) {
+	return m.endBlockResp, nil
+}
+
+func (m *mockABCIApplicationClient) Commit(_ context.Context, _ *abciv1.RequestCommit, _ ...grpc.CallOption) (*abciv1.ResponseCommit, error) {
+	return m.commitResp, nil
+}
```
