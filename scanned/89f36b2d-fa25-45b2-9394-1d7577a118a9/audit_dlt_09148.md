# [?] Avoid a race condition where DeployContract() returns before PendingNonce has been incremented (#15579)

## Summary
Severity: Unknown
Chain: Chainlink
Component: smartcontractkit/chainlink
Published: 2024-12-10
Source: https://github.com/smartcontractkit/chainlink/commit/10ef5a440c9eac58e90eec6eefe02bf37232e309
Type: security-commit

## Details
Avoid a race condition where DeployContract() returns before PendingNonce has been incremented (#15579)

## Patch
### core/chains/evm/logpoller/helper_test.go
```diff
@@ -118,11 +118,19 @@ func SetupTH(t testing.TB, opts logpoller.Opts) TestHarness {
 		opts.PollPeriod = 1 * time.Hour
 	}
 	lp := logpoller.NewLogPoller(o, esc, lggr, headTracker, opts)
+
+	pendingNonce, err := backend.Client().PendingNonceAt(testutils.Context(t), owner.From)
+	require.NoError(t, err)
+
+	owner.Nonce = big.NewInt(0).SetUint64(pendingNonce)
 	emitterAddress1, _, emitter1, err := log_emitter.DeployLogEmitter(owner, backend.Client())
 	require.NoError(t, err)
+
+	owner.Nonce.Add(owner.Nonce, big.NewInt(1)) // Avoid race where DeployLogEmitter returns before PendingNonce has been incremented
 	emitterAddress2, _, emitter2, err := log_emitter.DeployLogEmitter(owner, backend.Client())
 	require.NoError(t, err)
 	backend.Commit()
+	owner.Nonce = nil // Just use pending nonce after this
 
 	return TestHarness{
 		Lggr:            lggr,
```
