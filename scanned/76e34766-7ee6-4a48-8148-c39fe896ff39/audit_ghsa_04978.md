# [H] Klever-Go KVM: Hash-array amplification in P2P resolver request handling

## Summary
Severity: High
Advisory: GHSA-w342-mj6g-v9c4
CVE: CVE-2026-47249
CWE: CWE-400
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-06-05
Source: https://github.com/advisories/GHSA-w342-mj6g-v9c4
Type: github-advisory

## Affected
- Go: `github.com/klever-io/klever-go` — affected >=0 <1.7.18

## Details
### Summary
A connected peer can send a compressed `RequestDataType_HashArrayType` direct request that is only `442` bytes on the wire but expands into `200000` decoded hash entries inside the resolver path. On `klever-go` `v1.7.17`, this allows remote memory and CPU amplification against nodes that accept P2P peer connections.

### Details
Resolver antiflood logic accounts only one logical message and the compressed wire size in `data/retriever/resolvers/messageProcessor.go#L30`.

`Batch.Decompress()` in `data/batch/batch.go#L122` enforces an inflated byte cap but does not enforce a decoded repeated-field item cap. After decompression, `TxResolver` preallocates and iterates all decoded hashes in `data/retriever/resolvers/transactionResolver.go#L194`, and `TrieNodeResolver` iterates the same unchecked decoded set in `data/retriever/resolvers/trieNodeResolver.go#L108`.

Pinned references:
- https://github.com/klever-io/klever-go/blob/333f6ec910906e227705fc5767dc897d8fbfc862/data/retriever/resolvers/messageProcessor.go#L30
- https://github.com/klever-io/klever-go/blob/333f6ec910906e227705fc5767dc897d8fbfc862/data/batch/batch.go#L122
- https://github.com/klever-io/klever-go/blob/333f6ec910906e227705fc5767dc897d8fbfc862/data/retriever/resolvers/transactionResolver.go#L194
- https://github.com/klever-io/klever-go/blob/333f6ec910906e227705fc5767dc897d8fbfc862/data/retriever/resolvers/trieNodeResolver.go#L108

This appears distinct from the public `CVE-2026-44697` / `GHSA-87m7-qffr-542v`, which covered `MultiDataInterceptor` compressed batch fan-in. This report concerns resolver request paths that remain reachable through real libp2p direct-send plumbing on `v1.7.17`.

### PoC
Reproduced with:

```bash
go run auditpoc/request_batch_hash_amplification_poc.go
go test github.com/klever-io/klever-go/auditpoc -run TestRequestBatchHashAmplification_DirectSendReachability -count=1
```

Observed output:

```text
request wire bytes: 442
fits direct-send limit (983040 bytes): true
tx resolver lookups: 200000
trie resolver lookups: 200000
heap delta before first tx lookup: 17.47 MiB
ok   github.com/klever-io/klever-go/auditpoc
```

The E2E harness registers the victim resolver on the request topic and sends the malicious payload through `SendToConnectedPeer()` to prove the work amplification survives the real direct-send path.

### Impact
A connected peer can convert a sub-kilobyte request into large decode-time memory pressure and synchronous CPU work on the target node. Repeated requests or several concurrent peers can degrade or exhaust validator resources, affecting node availability.

## References
- https://github.com/klever-io/klever-go/security/advisories/GHSA-w342-mj6g-v9c4
- https://github.com/klever-io/klever-go
- https://github.com/klever-io/klever-go/releases/tag/v1.7.18
