### Title
Head-of-queue stall in Vault OCR pending-queue `StateTransition` lets a single unprocessable request block all other users' vault requests - ([File: core/services/ocr2/plugins/vault/plugin.go])

### Summary
The `Carousel` report describes a class of bug where a FILO/FIFO queue is processed strictly in order, and a single early entry that fails to satisfy a consensus/validation condition causes the loop to abort, permanently blocking every entry queued behind it. The Chainlink Vault OCR3 reporting plugin's `StateTransition` implements the same structural pattern for its pending request queue: it walks `idsToProcess` in order and calls `break` as soon as it hits an item that cannot reach the required observation consensus, leaving every subsequent (unrelated, honestly-submitted) request stuck behind it.

### Finding Description
`ReportingPlugin.StateTransition` in `core/services/ocr2/plugins/vault/plugin.go` processes `pendingQueueItems` (populated by ordinary, unprivileged `CreateSecrets`/`GetSecrets`/`DeleteSecrets`/`ListSecretIdentifiers` requests written to the OCR3 KV pending queue) strictly in FIFO order via `idsToProcess`.

For each `id` in the queue: [1](#0-0) 
- If observations for the head item are missing, it explicitly `break`s "since we know any other requests in the pending queue can't be processed." [2](#0-1) 
- If the item does not have `2F+1` matching "ok" observations (and does not have `F+1` matching error contributions, which triggers rejection instead), it again `break`s, halting all further processing for that round. [3](#0-2) 
- Similarly, if no sha reaches the required threshold of identical observations, the loop `break`s.

This is structurally identical to the `Carousel.mintDepositInQueue` bug: processing is done strictly in queue order, and any item that cannot be resolved (whether due to a malicious/inconsistent submitter, a config change, or a genuinely non-deterministic node response) blocks resolution of every item behind it in the same queue, not just the offending one.

The codebase clearly anticipated this exact failure mode — a `pendingQueueStallTracker` / `PendingQueueStallSignal` mechanism exists specifically to detect when nodes repeatedly fail to reach quorum on the head of the queue and to trigger `purgeStalledPendingQueue` as a release valve: [4](#0-3) 

However, this mitigation is bounded by a *threshold* (`VaultPendingQueueStallThreshold`, a rate/upper-bound limiter) — the stall signal only fires after the queue has failed to progress across some number of rounds: [5](#0-4) 

During the window before the stall threshold is reached, every legitimate, unprivileged caller's Vault request (`CreateSecrets`, `GetSecrets`, `DeleteSecrets`, `ListSecretIdentifiers` — all reachable via the internet-facing gateway `GatewayHandler` in `core/capabilities/vault/gw_handler.go`) that happens to be queued behind the stalled item is delayed/blocked from completing, because `StateTransition` refuses to make progress past the head.

### Impact Explanation
An unprivileged client (any workflow/user allowed by the Vault allowlist/JWT authorizer to submit `vault.secrets.*` requests through the gateway) can enqueue a request that is difficult or impossible for nodes to agree on (e.g., crafted so that observations split roughly evenly and never reach `2F+1` OK or `F+1` error consensus within the stall-detection window). Because processing is head-of-queue blocking, this delays/denies service for every other tenant's pending secret create/get/delete/list requests that were queued after it, until the stall-detection threshold trips and the queue is purged. This is a cross-tenant availability impact directly analogous to the Sherlock finding's "funds locked until fixed" — here it is "other users' vault requests denied until the stall purge kicks in."

### Likelihood Explanation
Reaching this path requires only an authorized-but-unprivileged Vault caller (workflow owner / gateway user), not a malicious node or operator — it is directly reachable through the standard `vault.secrets.*` JSON-RPC surface via the gateway, satisfying the "unprivileged actor" requirement. However, the severity is capped by the existing `pendingQueueStallTracker`/`purgeStalledPendingQueue` mitigation, which the team explicitly built to bound how long a stuck head-of-queue item can block the rest of the queue. The residual risk is bounded to the configured stall-detection window (`VaultPendingQueueStallThreshold`) rather than being unbounded/permanent, unlike the original `Carousel` bug.

### Recommendation
- Consider making pending-queue processing resilient to a single unresolvable head item without relying solely on the stall-signal/purge mechanism — e.g., skip/quarantine an item that cannot reach consensus after a bounded number of attempts instead of `break`-ing the entire batch, so well-formed requests behind it are not penalized.
- Ensure `VaultPendingQueueStallThreshold` defaults are tuned conservatively enough that legitimate concurrent Vault users are not meaningfully starved by a single adversarial or malformed request, and add metrics/alerts (the codebase already tracks `trackObservationPrefixCoverageSpread` / `trackObservationPrefixCoverage`) specifically for "queue blocked by single item" scenarios so operators can detect and react quickly.

### Proof of Concept
Not independently reproducible from static analysis alone — this requires running the OCR3 Vault plugin across a simulated DON, submitting a crafted secret request designed to produce split/inconsistent node observations, and observing that `StateTransition`'s loop (`core/services/ocr2/plugins/vault/plugin.go`, lines ~1611–1709) `break`s on that item across multiple rounds, delaying all subsequently queued requests until `countPendingQueueStallSignalsInMap(...) >= r.onchainCfg.F+1` triggers `purgeStalledPendingQueue`. The existing test `TestObservationQuorum_PendingQueueStallSignal` in `core/services/ocr2/plugins/vault/pending_queue_stall_test.go` (lines 133–162) demonstrates the underlying mechanics of this stall/continue signal path, confirming the head-of-queue blocking behavior exists and is bounded only by the stall-detection threshold.

### Citations

**File:** core/services/ocr2/plugins/vault/plugin.go (L1428-1436)
```go
func (r *ReportingPlugin) ObservationQuorum(ctx context.Context, seqNr uint64, aq types.AttributedQuery, aos []types.AttributedObservation, keyValueReader ocr3_1types.KeyValueStateReader, blobFetcher ocr3_1types.BlobFetcher) (quorumReached bool, err error) {
	if !quorumhelper.ObservationCountReachesObservationQuorum(quorumhelper.QuorumTwoFPlusOne, r.onchainCfg.N, r.onchainCfg.F, aos) {
		return false, nil
	}

	if countPendingQueueStallSignals(aos) >= r.onchainCfg.F+1 {
		return true, nil
	}

```

**File:** core/services/ocr2/plugins/vault/plugin.go (L1566-1568)
```go
	if stallSignalCount := countPendingQueueStallSignalsInMap(marshalledObs); stallSignalCount >= r.onchainCfg.F+1 {
		return r.purgeStalledPendingQueue(ctx, l, writeKV, stallSignalCount)
	}
```

**File:** core/services/ocr2/plugins/vault/plugin.go (L1615-1622)
```go
	for _, id := range idsToProcess {
		obs, ok := obsMap[id]
		// This can only happen if the pending queue item is not in the obsMap
		// at which point we know any other requests in the pending queue can't be processed so we can break.
		if !ok {
			r.lggr.Warnw("no observations for pending queue item; stopping state transition pending queue processing", "id", id)
			break
		}
```

**File:** core/services/ocr2/plugins/vault/plugin.go (L1653-1661)
```go
		if len(okObs) < 2*f+1 {
			r.lggr.Warnw("insufficient ok observations for pending queue item; stopping state transition",
				"id", id,
				"okCount", len(okObs),
				"errCount", len(errObs),
				"threshold", 2*f+1,
			)
			break
		}
```

**File:** core/services/ocr2/plugins/vault/plugin.go (L1702-1709)
```go
		if len(chosen) == 0 {
			shaToObsCount := map[string]int{}
			for sha, obs := range shaToObs {
				shaToObsCount[sha] = len(obs)
			}
			l.Warnw("insufficient observations found for requestID", "requestID", id, "shaToObsCount", shaToObsCount)
			break
		}
```
