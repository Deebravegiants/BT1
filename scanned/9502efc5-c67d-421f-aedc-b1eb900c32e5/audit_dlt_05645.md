# [?] [SharovBot] Fix data race in ExecModuleTester.SendMessageToRandomPeers (#19713)

## Summary
Severity: Unknown
Chain: Ethereum
Component: erigontech/erigon
Published: 2026-03-07
Source: https://github.com/erigontech/erigon/commit/6a1f2077f636005d510bc13fe84b5a4f408a4766
Type: security-commit

## Details
[SharovBot] Fix data race in ExecModuleTester.SendMessageToRandomPeers (#19713)

## Summary
- Add `sentMessagesMu` mutex to `ExecModuleTester` to protect concurrent
access to the `sentMessages` slice
- Guard all append operations in `SendMessageByMinBlock`,
`SendMessageById`, `SendMessageToRandomPeers`, and `SendMessageToAll`
with the mutex
- Guard read access in `SentMessage` with the mutex
- Fixes data race detected in `TestAssembleBlockWithFreshlyAddedTxns`
where `BroadcastPooledTxns` and `AnnouncePooledTxns` concurrently call
`SendMessageToRandomPeers`

## Test plan
- [x] `go test -race ./execution/execmodule/... -count=3 -run
TestAssembleBlockWithFreshlyAddedTxns` passes with no DATA RACE warnings
- [x] `go build ./...` passes
- [x] No `*_test.go` files modified

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-authored-by: Claude Opus 4.6 <noreply@anthropic.com>

## Patch
### execution/execmodule/execmoduletester/exec_module_tester.go
```diff
@@ -120,6 +120,7 @@ type ExecModuleTester struct {
 	SentryClient    direct.SentryClient
 	PeerId          *typesproto.H512
 	streams         map[sentryproto.MessageId][]sentryproto.Sentry_MessagesServer
+	sentMessagesMu  sync.Mutex
 	sentMessages    []*sentryproto.OutboundMessageData
 	StreamWg        sync.WaitGroup
 	ReceiveWg       sync.WaitGroup
@@ -198,22 +199,32 @@ func (emt *ExecModuleTester) HandShake(ctx context.Context, in *emptypb.Empty) (
 	return &sentryproto.HandShakeReply{Protocol: sentryproto.Protocol_ETH69}, nil
 }
 func (emt *ExecModuleTester) SendMessageByMinBlock(_ context.Context, r *sentryproto.SendMessageByMinBlockRequest) (*sentryproto.SentPeers, error) {
+	emt.sentMessagesMu.Lock()
 	emt.sentMessages = append(emt.sentMessages, r.Data)
+	emt.sentMessagesMu.Unlock()
 	return nil, nil
 }
 func (emt *ExecModuleTester) SendMessageById(_ context.Context, r *sentryproto.SendMessageByIdRequest) (*sentryproto.SentPeers, error) {
+	emt.sentMessagesMu.Lock()
 	emt.sentMessages = append(emt.sentMessages, r.Data)
+	emt.sentMessagesMu.Unlock()
 	return nil, nil
 }
 func (emt *ExecModuleTester) SendMessageToRandomPeers(_ context.Context, r *sentryproto.SendMessageToRandomPeersRequest) (*sentryproto.SentPeers, error) {
+	emt.sentMessagesMu.Lock()
 	emt.sentMessages = append(emt.sentMessages, r.Data)
+	emt.sentMessagesMu.Unlock()
 	return nil, nil
 }
 func (emt *ExecModuleTester) SendMessageToAll(_ context.Context, r *sentryproto.OutboundMessageData) (*sentryproto.SentPeers, error) {
+	emt.sentMessagesMu.Lock()
 	emt.sentMessages = append(emt.sentMessages, r)
+	emt.sentMessagesMu.Unlock()
 	return nil, nil
 }
 func (emt *ExecModuleTester) SentMessage(i int) (*sentryproto.OutboundMessageData, error) {
+	emt.sentMessagesMu.Lock()
+	defer emt.sentMessagesMu.Unlock()
 	if i < 0 || i >= len(emt.sentMessages) {
 		return nil, fmt.Errorf("no sent message for index %d found", i)
 	}
```
