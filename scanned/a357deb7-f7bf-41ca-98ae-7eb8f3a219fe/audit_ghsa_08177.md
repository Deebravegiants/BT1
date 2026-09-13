# [M] zae-limiter: DynamoDB hot partition throttling enables per-entity Denial of Service

## Summary
Severity: Medium
Advisory: GHSA-76rv-2r9v-c5m6
CVE: CVE-2026-27695
CWE: CWE-770
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:L (CVSS_V3)
Published: 2026-02-25
Source: https://github.com/advisories/GHSA-76rv-2r9v-c5m6
Type: github-advisory

## Affected
- PyPI: `zae-limiter` — affected >=0 <0.10.1

## Details
## Summary

All rate limit buckets for a single entity share the same DynamoDB partition key (`namespace/ENTITY#{id}`). A high-traffic entity can exceed DynamoDB's per-partition throughput limits (~1,000 WCU/sec), causing throttling that degrades service for that entity — and potentially co-located entities in the same partition.

## Details

Each `acquire()` call performs a `TransactWriteItems` (or `UpdateItem` in speculative mode) against items sharing the same partition key. For cascade entities, this doubles to 2-4 writes per request (child + parent). At sustained rates above ~500 req/sec for a single entity, DynamoDB's adaptive capacity may not redistribute fast enough, causing `ProvisionedThroughputExceededException`.

The library has no built-in mitigation:
- No partition key sharding/salting
- No write coalescing or batching
- No client-side admission control before hitting DynamoDB
- `RateLimiterUnavailable` is raised but the caller has already been delayed

## Impact

- **Availability**: High-traffic entities experience elevated latency and rejected requests beyond what their rate limits specify
- **Fairness**: Other entities sharing the same DynamoDB partition may experience collateral throttling
- **Multi-tenant risk**: In a shared LLM proxy scenario, one tenant's burst traffic could degrade service for others

## Reproduction

1. Create an entity with high rate limits (e.g., 100,000 rpm)
2. Send sustained traffic at 1,000+ req/sec to a single entity
3. Observe DynamoDB `ThrottledRequests` CloudWatch metric increasing
4. Observe `acquire()` latency spikes and `RateLimiterUnavailable` exceptions

## Remediation Design: Pre-Shard Buckets

- Move buckets to `PK={ns}/BUCKET#{entity}#{resource}#{shard}, SK=#STATE` — one partition per (entity, resource, shard)
- Auto-inject `wcu:1000` reserved limit on every bucket — tracks DynamoDB partition write pressure in-band (name may change during implementation)
- Shard doubling (1→2→4→8) triggered by client on `wcu` exhaustion or proactively by aggregator
- Shard 0 at suffix `#0` is source of truth for `shard_count`. Aggregator propagates to other shards
- Original limits stored on bucket, effective limits derived: `original / shard_count`. Infrastructure limits (`wcu`) not divided
- Shard selection: random/round-robin. On application limit exhaustion, retry on another shard (max 2 retries)
- Lazy shard creation on first access
- Bucket discovery via GSI3 (KEYS_ONLY) + BatchGetItem. GSI2 for resource aggregation unchanged
- Cascade: parent unaware, protected by own `wcu`
- Aggregator: parse new PK format, key by shard_id, effective limits for refill, filter `wcu` from snapshots
- Clean break migration: schema version bump, old buckets ignored, new buckets created on first access
- **$0.625/M preserved on hot path**

## References
- https://github.com/zeroae/zae-limiter/security/advisories/GHSA-76rv-2r9v-c5m6
- https://nvd.nist.gov/vuln/detail/CVE-2026-27695
- https://github.com/zeroae/zae-limiter/commit/481ce44d818d66e31d8837bc48519660ce4c267f
- https://github.com/zeroae/zae-limiter
- https://github.com/zeroae/zae-limiter/releases/tag/v0.10.1
