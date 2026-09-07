# [M] Uprobe gadgets: unprivileged container's ld.so.cache causes high CPU utilization and container startup DoS

## Summary
Severity: Medium
Advisory: GHSA-vjhx-2cqw-3q6q
CVE: CVE-2026-53941
CWE: CWE-400, CWE-770
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:L/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-08-19
Source: https://github.com/advisories/GHSA-vjhx-2cqw-3q6q
Type: github-advisory

## Affected
- Go: `github.com/inspektor-gadget/inspektor-gadget` — affected >=0.27.0 <0.53.1

## Details
## Summary

An unprivileged container can block all other containers from starting on the
same host by placing a crafted `/etc/ld.so.cache` file in its filesystem. When
Inspektor Gadget attaches any uprobe-based gadget, it parses this file in the
container startup path. A malicious cache causes ~53 seconds of CPU burn,
during which Docker cannot start any other container. No special capabilities
are required.

## Severity

To be assessed — Availability impact, no confidentiality or integrity impact.

## Affected Versions

All versions of Inspektor Gadget that support uprobe-based gadgets (trace_malloc, trace_open, trace_ssl, trace_grpc, etc.).

## Description

When Inspektor Gadget attaches uprobe-based gadgets to containers, it resolves library paths by parsing the container's `/etc/ld.so.cache` file (`pkg/uprobetracer/ldcache_parser.go`). This file is fully controlled by the container.

The parser has three vulnerabilities:

1. **Quadratic string building** (`pkg/uprobetracer/bytes.go:36-44`): The `readStringFromBytes` function concatenates one byte at a time (`res += string(data[i])`), which is O(n²) in Go due to string immutability. With a 16MB cache file containing large regions without null terminators, this causes massive CPU and memory churn.

2. **Insufficient entry count validation** (`pkg/uprobetracer/ldcache_parser.go:120`): The `EntryCount` field is read directly from the untrusted file. While a per-entry bounds check prevents out-of-bounds access, the loop still iterates up to `(fileSize - headerSize) / entrySize ≈ 700,000` times, calling `readStringFromBytes` on each iteration.

3. **Integer overflow in format detection** (`pkg/uprobetracer/ldcache_parser.go:174`): The `cache1Len` computation uses uint32 arithmetic (`ldCache1Size + cache1.EntryCount*ldCache1EntrySize`). With a crafted `EntryCount`, this overflows and produces a small value, causing the parser to misidentify the cache format.

Combined, these cause ~53 seconds of CPU burn per container attachment when a crafted 16MB `/etc/ld.so.cache` is present.

## Impact

- **Container runtime DoS**: IG uses fanotify hooks (`pkg/container-hook`) to pause container startup until uprobe attachment completes. While IG is blocked processing the malicious cache, this pause is held, and Docker serializes container starts — meaning no other container can start on the host until IG finishes. This effectively causes a denial of service on the entire container runtime, not just on IG itself.
- **Container startup delay**: When any uprobe-based gadget is running (trace_malloc, trace_ssl, etc.), starting a container with a crafted ld.so.cache delays startup by ~1 minute.
- **Monitoring degradation**: The IG daemon is blocked processing the malicious cache, potentially missing events from other containers.
- **Amplification**: Multiple containers with crafted caches can be started simultaneously to amplify the effect.
- **No special privileges required**: Any container can include a crafted `/etc/ld.so.cache` in its image, mount one via a volume, or overwrite it at runtime before IG starts a uprobe gadget. In this last case, IG inspects all already-running containers when the gadget starts — this still burns CPU but does not block other containers from starting (since the fanotify pause only applies to new container starts).

## Root Cause Analysis

In `pkg/uprobetracer/ldcache_parser.go`, the function `readCacheFormat2` is called with the full file content:

```go
for i := uint32(0); i < ldCache.EntryCount; i++ {
    entryOffset := ldEntriesOffset + i*ldCache2EntrySize
    if uint32(len(data)) <= entryOffset+ldCache2EntrySize {
        return nil  // bounds check stops iteration
    }
    // ... reads entry ...
    key := readStringFromBytes(data, keyOffset)    // O(n²) per call
    value := readStringFromBytes(data, valueOffset) // O(n²) per call
}
```

The per-entry bounds check correctly prevents out-of-bounds access, but:
- The loop iterates ~700K times (limited by file size, not EntryCount)
- Each `readStringFromBytes` call uses quadratic string concatenation

In `pkg/uprobetracer/bytes.go`:

```go
func readStringFromBytes(data []byte, startPos uint32) string {
    res := ""
    for i := startPos; i < uint32(len(data)); i++ {
        if data[i] == 0 {
            return res
        }
        res += string(data[i])  // O(n²) — allocates new string each iteration
    }
    return ""
}
```

## Note on Slice Bounds Checks

The code also performs slice accesses without proper bounds checks (e.g.,
`data[:len(cache2Header)]` when `data` may be shorter than 20 bytes, and
`ldCacheFile[:len(cache1Header)]` when the file may be shorter than 11 bytes).

In practice, a malicious container **cannot currently trigger a panic** from these
missing checks. This is because Go's `io.ReadAll` (used to read the file) always
returns slices with `cap >= 512` due to its initial buffer allocation
(`make([]byte, 0, 512)` in Go's standard library). In Go, `s[:n]` only panics
when `n > cap(s)`, not when `n > len(s)`. Since both header lengths (11 and 20)
are well below 512, the slice expressions succeed — they simply read zero bytes
beyond `len`, which don't match any valid header magic.

However, this relies on an **undocumented implementation detail** of `io.ReadAll`
which could change in future Go versions. The bounds checks are still necessary
for correctness and defense in depth.

## References
- https://github.com/inspektor-gadget/inspektor-gadget/security/advisories/GHSA-vjhx-2cqw-3q6q
- https://github.com/inspektor-gadget/inspektor-gadget
- https://github.com/inspektor-gadget/inspektor-gadget/releases/tag/v0.53.1
