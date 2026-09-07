# [?] fix: IByteBuffer leak in EnrResponseMsgSerializer & ArrayPoolSpan OOB (#10853)

## Summary
Severity: Unknown
Chain: Ethereum
Component: NethermindEth/nethermind
Published: 2026-03-18
Source: https://github.com/NethermindEth/nethermind/commit/fca448c9239e5dfb6edbb743c443b6b3d3b3e460
Type: security-commit

## Details
fix: IByteBuffer leak in EnrResponseMsgSerializer & ArrayPoolSpan OOB (#10853)

* fix leak & array oob

* add leak detector

* Add claude rule

* remove docs

* fix formatting & add allocator cost note to LeakDetector

* fix: address PR review feedback

- ArrayPoolSpan.Slice: validate against logical length, not rented array
- ArrayPoolSpan indexer: add nameof(index) to ThrowIfGreaterThanOrEqual
- Add Slice tests: boundary, out-of-range, and logical length enforcement
- PooledBufferLeakDetector: add AssertNoLeaks() for explicit assertion,
  make Dispose() non-throwing to avoid masking test-body exceptions
- Add explicit FluentAssertions package reference to Discovery.Test csproj
- Add buffer refcount leak tests for all discovery message serializers
  (Ping, Pong, FindNode, Neighbors, EnrResponse — happy and error paths)
- Fix leak test: use ReferenceCount check instead of PooledBufferLeakDetector
  (pool NumActiveAllocations metric is unreliable with zero-cache config)

---------

Co-authored-by: Ben Adams <thundercat@illyriad.co.uk>
