# [M] Netty: RedisArrayAggregator max-elements failure leaves retained partial aggregate state

## Summary
Severity: Medium
Advisory: GHSA-p9jm-q85p-7mcp
CVE: CVE-2026-56818
CWE: CWE-401, CWE-703
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:L (CVSS_V3)
Published: 2026-08-07
Source: https://github.com/advisories/GHSA-p9jm-q85p-7mcp
Type: github-advisory

## Affected
- Maven: `io.netty:netty-codec-redis` — affected >=0 <4.1.136.Final
- Maven: `io.netty:netty-codec-redis` — affected >=4.2.0-Final <4.2.16.Final

## Details
## Summary

`RedisArrayAggregator` clears retained partial aggregate state when the `maxNestedArrayDepth` limit is exceeded, but it does not clear the same state when the sibling `maxElements` limit is exceeded. A peer can start a valid RESP array, send a bulk-string child, then send a nested array header longer than the configured `maxElements`. Netty throws a decoder exception, but the existing partial aggregate remains retained in the handler.

If the application leaves the channel alive after the exception, later messages are still consumed into the pre-error aggregate. The supplied PoV proves both the retained `ByteBuf` reference and the stale parser state continuation.

## Technical Details

`RedisArrayAggregator.decode(...)` retains non-array messages before adding them to `depths.peek().children`. In `decodeRedisArrayHeader(...)`, the `header.length() > maxElements` branch throws immediately:

```java
if (header.length() > maxElements) {
    throw new CodecException("this codec doesn't support longer length than " + maxElements);
}
```

The immediately following nested-depth branch clears retained aggregate state before throwing:

```java
if (depths.size() >= maxNestedArrayDepth) {
    releaseAndClearDepths();
    throw new CodecException("max nested array depth exceeded: " + maxNestedArrayDepth);
}
```

The missing cleanup in the first branch leaves retained children and aggregate state reachable after the exception.

## PoC

Place the supplied `RedisArrayAggregatorIncompleteCleanupPovTest.java` under:

`codec-redis/src/test/java/io/netty/handler/codec/redis/`

Run:

```fish
./mvnw -pl codec-redis -am -Dtest=RedisArrayAggregatorIncompleteCleanupPovTest -Dsurefire.failIfNoSpecifiedTests=false -DskipNativeTests -DskipAutobahnTests test
```

The test suite includes:

- serialized RESP trigger through `RedisDecoder`, `RedisBulkStringAggregator`, and `RedisArrayAggregator`;
- direct refcount proof that max-elements overflow does not release the retained child immediately;
- post-exception continuation proof that the stale aggregate consumes a later message;
- nested-depth controls that clear the same partial aggregate state.

All five tests pass on current `4.2`, `4.2.15.Final`, and `4.1.135.Final`.

## Impact

For Redis codec pipelines that continue after codec exceptions, an unauthenticated peer can keep attacker-controlled aggregate state alive across a security-limit exception. This can pin retained pooled buffers until channel close/removal or until a later message completes the stale aggregate.

`RedisBulkStringAggregator` permits bulk strings up to `RedisConstants.REDIS_MESSAGE_MAX_LENGTH` (`512MB`), so the retained child can be large in deployments that aggregate untrusted Redis streams.

Applications that always close the channel or remove the handler on decoder exceptions will trigger existing cleanup; the issue is the missing immediate cleanup on the max-elements failure path while the handler remains installed.

## Suggested Fix

Call `releaseAndClearDepths()` before throwing from the max-elements branch. Consider applying the same cleanup to all unrecoverable `decodeRedisArrayHeader(...)` error exits that can occur while `depths` is non-empty.

## Affected Package/Versions

`io.netty:netty-codec-redis`

Confirmed on:

- current `4.2` branch head `7bae566a93e69409697fe57fa807910ba5c9720e`
- `4.2.15.Final` at `a41f7b289ce1`
- `4.1.135.Final` at `f05f765d8146`

## Advisory History

This differs from the public Redis codec advisories because it reproduces on their patched tags:

- `GHSA-5w86-c3rq-vjj7`
- `GHSA-3244-j874-rhc2` / `CVE-2026-44250`
- `GHSA-6jv9-x5w9-2ccm` / `CVE-2026-48006`
- `GHSA-6ghj-frrj-jjj3` / `CVE-2026-44890`

## Why This Is Not Intended Behavior

The public API docs document `RedisArrayAggregator` as aggregating `RedisMessage` parts into `ArrayRedisMessage` and document a `CodecException` when an array header exceeds `maxElements`. They do not document preserving pre-exception partial aggregate state after that limit fires.

The adjacent nested-depth branch already calls `releaseAndClearDepths()` before throwing. The max-elements branch is the sibling aggregation-limit branch but throws without cleanup. Netty's later Redis lifecycle cleanup patch explicitly added release behavior for nested-array failure and handler removal, leaving the max-elements failure branch as a missed cleanup path.

## References
- https://github.com/netty/netty/security/advisories/GHSA-p9jm-q85p-7mcp
- https://github.com/netty/netty/pull/17065
- https://github.com/netty/netty/commit/5b68c61f37aa4a3045cba624cbea239655c9003b
- https://github.com/netty/netty/commit/bb2ff68a1fb71cb4b0eb9a9e17b66c52aff680c6
- https://github.com/netty/netty
