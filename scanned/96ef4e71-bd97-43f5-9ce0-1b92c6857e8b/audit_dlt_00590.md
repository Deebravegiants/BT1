# [?] Fix nil pointer dereference in validator client with non-Prysm beacon-nodes (#16449)

## Summary
Severity: Unknown
Chain: Ethereum
Component: prysmaticlabs/prysm
Published: 2026-03-02
Source: https://github.com/OffchainLabs/prysm/commit/544bc3eb45cdddeb791c44b5b27b40670bbf8abf
Type: security-commit

## Details
Fix nil pointer dereference in validator client with non-Prysm beacon-nodes (#16449)

1. When connecting to a REST-only beacon node (e.g. Teku, Lighthouse),
the gRPC connection provider is nil. The grpcClientManager was
unconditionally calling ConnectionCounter() on the provider in both
newGrpcClientManager and getClient, causing a SIGSEGV panic on startup.
2. runner.go — Made initial PushProposerSettings non-fatal. Lighthouse
returns 500: UnableToReadSlot on
/eth/v1/validator/prepare_beacon_proposer at genesis (slot 0) before any
blocks exist. The run loop already handles this as a warning — now the
initial call does too, and it retries on the next slot.


to repro the bug:
```yaml
participants:
  - el_type: geth
    el_image: ethpandaops/geth:master
    cl_type: prysm
    cl_image: ethpandaops/prysm-beacon-chain:develop
    vc_type: prysm
    vc_image: ethpandaops/prysm-validator:develop
    count: 1
  - el_type: geth
    el_image: ethpandaops/geth:master
    cl_type: teku
    cl_image: ethpandaops/teku:master
    vc_type: prysm
    vc_image: ethpandaops/prysm-validator:develop
    count: 1
additional_services:
  - dora
```

To repro the fix: 
```yaml
participants:
  - el_type: geth
    el_image: ethpandaops/geth:master
    cl_type: prysm
    cl_image: ethpandaops/prysm-beacon-chain:develop
    vc_type: prysm
    vc_image: ethpandaops/prysm-validator:develop
    count: 1
  - el_type: geth
    el_image: ethpandaops/geth:master
    cl_type: teku
    cl_image: ethpandaops/teku:master
    vc_type: prysm
    vc_image: ethpandaops/prysm-validator:barnabasbusa-bbusa-vc-fix
    count: 1
  - el_type: geth
    el_image: ethpandaops/geth:master
    cl_type: lighthouse
    cl_image: ethpandaops/lighthouse:unstable
    vc_type: prysm
    vc_image: ethpandaops/prysm-validator:barnabasbusa-bbusa-vc-fix
    count: 1


additional_services:
  - dora

```



**What type of PR is this?**

> Uncomment one line below and remove others.
>
> Bug fix
> Feature
> Documentation
> Other

**What does this PR do? Why is it needed?**

**Which issues(s) does this PR fix?**

Fixes #

**Other notes for review**

**Acknowledgements**

- [X] I have read
[CONTRIBUTING.md](https://github.com/prysmaticlabs/prysm/blob/develop/CONTRIBUTING.md).
- [X] I have included a uniquely named [changelog fragment
file](https://github.com/prysmaticlabs/prysm/blob/develop/CONTRIBUTING.md#maintaining-changelogmd).
- [X] I have added a description with sufficient context for reviewers
to understand this PR.
- [X] I have tested that my changes work as expected and I added a
testing plan to the PR description (if applicable).

---------

Co-authored-by: Claude Opus 4.6 <noreply@anthropic.com>

### changelog/barnabasbusa_fix-vc-non-prysm-bn.md
```diff
@@ -0,0 +1,4 @@
+### Fixed
+
+- Fixed nil pointer dereference in validator client when connecting to non-Prysm beacon nodes (REST-only, no gRPC).
+- Made initial proposer settings push non-fatal so the validator runner can start even if the beacon node is not yet ready at genesis.
```

### validator/client/grpc-api/grpc_client_manager.go
```diff
@@ -22,11 +22,15 @@ func newGrpcClientManager[T any](
 	conn validatorHelpers.NodeConnection,
 	newClient func(grpc.ClientConnInterface) T,
 ) *grpcClientManager[T] {
+	var lastConnCounter uint64
+	if provider := conn.GetGrpcConnectionProvider(); provider != nil {
+		lastConnCounter = provider.ConnectionCounter()
+	}
 	return &grpcClientManager[T]{
 		conn:            conn,
 		newClient:       newClient,
 		client:          newClient(conn.GetGrpcClientConn()),
-		lastConnCounter: conn.GetGrpcConnectionProvider().ConnectionCounter(),
+		lastConnCounter: lastConnCounter,
 	}
 }
 
@@ -38,7 +42,11 @@ func (m *grpcClientManager[T]) getClient() T {
 	m.mu.Lock()
 	defer m.mu.Unlock()
 
-	currentCounter := m.conn.GetGrpcConnectionProvider().ConnectionCounter()
+	provider := m.conn.GetGrpcConnectionProvider()
+	if provider == nil {
+		return m.client
+	}
+	currentCounter := provider.ConnectionCounter()
 	if m.lastConnCounter != currentCounter {
 		m.client = m.newClient(m.conn.GetGrpcClientConn())
 		m.lastConnCounter = currentCounter
```

### validator/client/runner.go
```diff
@@ -64,8 +64,7 @@ func newRunner(ctx context.Context, v iface.Validator, monitor *healthMonitor) (
 			" and will continue to use settings provided in the beacon node.")
 	}
 	if err := v.PushProposerSettings(ctx, currentSlot, true); err != nil {
-		v.Done()
-		return nil, errors.Wrap(err, "failed to update proposer settings")
+		log.WithError(err).Warn("Failed to push initial proposer settings, will retry on next slot")
 	}
 	return &runner{
 		validator:     v,
```
