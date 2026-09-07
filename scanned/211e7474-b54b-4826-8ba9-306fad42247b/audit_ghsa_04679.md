# [H] klever-go: Unbounded goroutine spawn on direct-message ingress enables peer-driven DoS

## Summary
Severity: High
Advisory: GHSA-hf2g-6j7h-98wg
CVE: CVE-2026-52879
CWE: CWE-400, CWE-770
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-06-05
Source: https://github.com/advisories/GHSA-hf2g-6j7h-98wg
Type: github-advisory

## Affected
- Go: `github.com/klever-io/klever-go` — affected >=1.7.14 <1.7.18

## Details
### Summary

`networkMessenger.directMessageHandler` in `network/p2p/libp2p/netMessenger.go` spawns a fresh goroutine for every incoming direct message before the antiflood layer makes an admission decision. There is no semaphore, throttler, or bound on concurrent in-flight spawns.

A single connected libp2p peer can open a `DirectSendID` stream and send well-formed `TopicMessage` envelopes with varying sequence numbers. Each accepted direct message reaches `directMessageHandler` and triggers a fresh goroutine before `processor.ProcessReceivedMessage` runs. This allows unbounded goroutine growth and node availability degradation from one peer.

This remains present in the latest release `v1.7.17`: `network/p2p/libp2p/netMessenger.go:1060` still spawns `go func(msg p2p.MessageP2P)` before `processor.ProcessReceivedMessage`. I also verified current `develop` commit `10bcfd50`, where the same spawn remains at `network/p2p/libp2p/netMessenger.go:1115`.

This is distinct from GHSA-74m6-4hjp-7226 and GHSA-87m7-qffr-542v. Those advisories concern `MultiDataInterceptor` decompression/throttler behavior. This report concerns the libp2p direct-message ingress wrapper spawning an unbounded goroutine before processor-level antiflood/admission logic runs. A patch to `Batch.Decompress` or `MultiDataInterceptor` does not bound this direct-message goroutine spawn.

### Details

The affected path is `network/p2p/libp2p/netMessenger.go` in `directMessageHandler`.

The direct-message path transforms and validates the message, looks up the topic processor, then immediately spawns a goroutine:

```go
func (netMes *networkMessenger) directMessageHandler(message *pubsub.Message, fromConnectedPeer core.PeerID) error {
    var processor p2p.MessageProcessor

    topic := *message.Topic
    msg, err := netMes.transformAndCheckMessage(message, fromConnectedPeer, topic)
    if err != nil {
        return err
    }

    netMes.mutTopics.RLock()
    processor = netMes.processors[topic]
    netMes.mutTopics.RUnlock()

    if processor == nil {
        return fmt.Errorf("%w on directMessageHandler for topic %s", p2p.ErrNilValidator, topic)
    }

    go func(msg p2p.MessageP2P) {
        if check.IfNil(msg) {
            return
        }

        errProcess := processor.ProcessReceivedMessage(msg, fromConnectedPeer)
        // ...
    }(msg)

    return nil
}
```

The processor-level antiflood decision happens inside `ProcessReceivedMessage`, after the goroutine, its stack, and the cloned message reference already exist. That means antiflood can bound processing rate, but not goroutine creation rate.

The existing `goRoutinesThrottler` with capacity `broadcastGoRoutines = 1000` is wired into outgoing broadcast paths such as `BroadcastOnChannelBlocking`, not this incoming direct-message path.

The parallel pubsub ingress path in the same file handles a comparable inbound message surface synchronously:

```go
err = handler.ProcessReceivedMessage(msg, fromConnectedPeer)
```

So the direct-message path is asymmetric: same transform/check function, same `ProcessReceivedMessage` callee, but direct-message ingress adds an unbounded goroutine spawn.

Reachability:

- `directSender.go` registers `DirectSendID` as a libp2p stream protocol.
- `directStreamHandler` reads framed `pubsub.Message` envelopes from the stream.
- `directStreamHandler` forwards each message to `networkMessenger.directMessageHandler`.
- Any connected peer can send well-formed envelopes to registered topics.
- The `seenMessages` cache keys on `From + Seqno`; `Seqno` is attacker-controlled in the envelope, so incrementing it bypasses dedupe.

### PoC

GitHub Private Vulnerability Reporting does not appear to allow file attachments in this form, so I am including the reproduction command and captured output inline. I can provide the full Go test file immediately if useful.

The PoC is a Go test file intended to be placed under `network/p2p/libp2p/` in a `klever-go` checkout. It exercises the real `network/p2p/libp2p` package with `NewMockMessenger`.

Reproduction:

```bash
git clone https://github.com/klever-io/klever-go
cd klever-go
git checkout v1.7.16

# Place dos_directmsg_test.go into:
# network/p2p/libp2p/

go test ./network/p2p/libp2p/ -run TestPoC_ -count=1 -v -timeout 60s
```

Captured output:

```text
=== RUN   TestPoC_DirectMessageHandler_SpawnsGoroutinePerMessage
    baseline goroutines: 43
    peak goroutines after 500 direct messages: 543 (delta = 500)
    final goroutines after drain + GC: 43
POC_RESULT direct=spawn N=500 baseline=43 peak=543 delta=500 threshold=400 final=43
--- PASS

=== RUN   TestPoC_SynchronousHandler_NoGoroutineGrowth
    baseline goroutines: 47
    peak goroutines after 500 synchronous calls: 47 (delta = 0)
POC_RESULT sync=block N=500 baseline=47 peak=47 delta=0
--- PASS

=== RUN   TestPoC_DirectMessageHandler_NoThrottlerInPath
    all 2000 SendToConnectedPeer calls returned in 2.490708ms -- no throttler blocking
POC_RESULT throttler=absent N=2000 elapsed=2.490708ms
--- PASS
```

Reading:

1. 500 direct messages with slow processors produced exactly 500 new goroutines.
2. The synchronous control path produced zero goroutine growth.
3. 2000 messages, twice the outgoing `broadcastGoRoutines = 1000` capacity, returned immediately, showing no ingress throttler blocks this path.

### Impact

A single connected peer can sustain unbounded goroutine spawn growth on a klever-go node. Each spawned goroutine allocates its own stack, holds message references until the processor returns, and adds scheduler and GC pressure before antiflood admission can reject the message.

Under realistic attacker line rate and non-trivial processor latency, goroutine count can grow faster than the runtime drains it, degrading the node's ability to process legitimate traffic. This maps to the `SECURITY.md` High category: "Denial of Service affecting network availability."

All testing was local only. I did not contact Klever mainnet, public testnet, hosted RPCs, explorers, or third-party production infrastructure.

Suggested fixes:

1. Wire `goRoutinesThrottler.CanProcess()` or a dedicated ingress throttler before the `go func()` spawn in `directMessageHandler`.
2. Or remove the goroutine and call `ProcessReceivedMessage` synchronously, matching the existing `pubsubCallback` path.

Disclosure note: I originally sent this report to `security@klever.org` on 2026-05-13. Since `SECURITY.md` lists GitHub Private Vulnerability Reporting as the recommended channel, I am resubmitting it here.

## References
- https://github.com/klever-io/klever-go/security/advisories/GHSA-hf2g-6j7h-98wg
- https://github.com/klever-io/klever-go
- https://github.com/klever-io/klever-go/releases/tag/v1.7.18
