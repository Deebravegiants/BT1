# [?] metrics: fix panic because of absent prometheus label (#9455)

## Summary
Severity: Unknown
Chain: Cosmos
Component: cometbft/cometbft
Published: 2022-09-21
Source: https://github.com/cometbft/cometbft/commit/f2c32c9b3ee00605e38010321d8d7d32e2d692c8
Type: security-commit

## Details
metrics: fix panic because of absent prometheus label (#9455)

Absence of this label causes a panic because the setters try to access the label despite it never being added to the metric. This PR adds the label to the metrics, thus preventing the panic.

#### PR checklist

- [ ] Tests written/updated, or no tests needed
- [ ] `CHANGELOG_PENDING.md` updated, or no changelog entry needed
- [ ] Updated relevant documentation (`docs/`) and code comments, or no
      documentation updates needed

## Patch
### consensus/metrics.gen.go
```diff
@@ -179,13 +179,13 @@ func PrometheusMetrics(namespace string, labelsAndValues ...string) *Metrics {
 			Subsystem: MetricsSubsystem,
 			Name:      "round_voting_power_percent",
 			Help:      "RoundVotingPowerPercent is the percentage of the total voting power received with a round. The value begins at 0 for each round and approaches 1.0 as additional voting power is observed. The metric is labeled by vote type.",
-		}, labels).With(labelsAndValues...),
+		}, append(labels, "vote_type")).With(labelsAndValues...),
 		LateVotes: prometheus.NewCounterFrom(stdprometheus.CounterOpts{
 			Namespace: namespace,
 			Subsystem: MetricsSubsystem,
 			Name:      "late_votes",
 			Help:      "LateVotes stores the number of votes that were received by this node that correspond to earlier heights and rounds than this node is currently in.",
-		}, labels).With(labelsAndValues...),
+		}, append(labels, "vote_type")).With(labelsAndValues...),
 	}
 }
 
```

### consensus/metrics.go
```diff
@@ -108,12 +108,12 @@ type Metrics struct {
 	// RoundVotingPowerPercent is the percentage of the total voting power received
 	// with a round. The value begins at 0 for each round and approaches 1.0 as
 	// additional voting power is observed. The metric is labeled by vote type.
-	RoundVotingPowerPercent metrics.Gauge
+	RoundVotingPowerPercent metrics.Gauge `metrics_labels:"vote_type"`
 
 	// LateVotes stores the number of votes that were received by this node that
 	// correspond to earlier heights and rounds than this node is currently
 	// in.
-	LateVotes metrics.Counter
+	LateVotes metrics.Counter `metrics_labels:"vote_type"`
 }
 
 // RecordConsMetrics uses for recording the block related metrics during fast-sync.
```

### p2p/metrics.gen.go
```diff
@@ -25,25 +25,25 @@ func PrometheusMetrics(namespace string, labelsAndValues ...string) *Metrics {
 			Subsystem: MetricsSubsystem,
 			Name:      "peer_receive_bytes_total",
 			Help:      "Number of bytes received from a given peer.",
-		}, labels).With(labelsAndValues...),
+		}, append(labels, "peer_id", "chID")).With(labelsAndValues...),
 		PeerSendBytesTotal: prometheus.NewCounterFrom(stdprometheus.CounterOpts{
 			Namespace: namespace,
 			Subsystem: MetricsSubsystem,
 			Name:      "peer_send_bytes_total",
 			Help:      "Number of bytes sent to a given peer.",
-		}, labels).With(labelsAndValues...),
+		}, append(labels, "peer_id", "chID")).With(labelsAndValues...),
 		PeerPendingSendBytes: prometheus.NewGaugeFrom(stdprometheus.GaugeOpts{
 			Namespace: namespace,
 			Subsystem: MetricsSubsystem,
 			Name:      "peer_pending_send_bytes",
 			Help:      "Pending bytes to be sent to a given peer.",
-		}, labels).With(labelsAndValues...),
+		}, append(labels, "peer_id")).With(labelsAndValues...),
 		NumTxs: prometheus.NewGaugeFrom(stdprometheus.GaugeOpts{
 			Namespace: namespace,
 			Subsystem: MetricsSubsystem,
 			Name:      "num_txs",
 			Help:      "Number of transactions submitted by each peer.",
-		}, labels).With(labelsAndValues...),
+		}, append(labels, "peer_id")).With(labelsAndValues...),
 	}
 }
 
```

### p2p/metrics.go
```diff
@@ -17,11 +17,11 @@ type Metrics struct {
 	// Number of peers.
 	Peers metrics.Gauge
 	// Number of bytes received from a given peer.
-	PeerReceiveBytesTotal metrics.Counter
+	PeerReceiveBytesTotal metrics.Counter `metrics_labels:"peer_id,chID"`
 	// Number of bytes sent to a given peer.
-	PeerSendBytesTotal metrics.Counter
+	PeerSendBytesTotal metrics.Counter `metrics_labels:"peer_id,chID"`
 	// Pending bytes to be sent to a given peer.
-	PeerPendingSendBytes metrics.Gauge
+	PeerPendingSendBytes metrics.Gauge `metrics_labels:"peer_id"`
 	// Number of transactions submitted by each peer.
-	NumTxs metrics.Gauge
+	NumTxs metrics.Gauge `metrics_labels:"peer_id"`
 }
```
