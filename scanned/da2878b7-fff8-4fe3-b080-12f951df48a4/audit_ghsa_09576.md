# [H] mercure has Topic Selector Cache Key Collision

## Summary
Severity: High
Advisory: GHSA-hwr4-mq23-wcv5
CVE: CVE-2026-39972
CWE: CWE-1289
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:N/VA:L/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-04-08
Source: https://github.com/advisories/GHSA-hwr4-mq23-wcv5
Type: github-advisory

## Affected
- Go: `github.com/dunglas/mercure` — affected >=0 <0.22.0

## Details
### Impact

A cache key collision vulnerability in `TopicSelectorStore` allows an attacker to poison the match result cache, potentially causing private updates to be delivered to unauthorized subscribers or blocking delivery to authorized ones.

The cache key was constructed by concatenating the topic selector and topic with an underscore separator:

```go
k = "m_" + topicSelector + "_" + topic
```

Because both topic selectors and topics can contain underscores, two distinct pairs can produce the same key:

```
selector="foo_bar"  topic="baz"     → key: "m_foo_bar_baz"
selector="foo"      topic="bar_baz" → key: "m_foo_bar_baz"
```

An attacker who can subscribe to the hub or publish updates with crafted topic names can exploit this to bypass authorization checks on private updates.

### Patches

The vulnerability is fixed by replacing string-encoded cache keys with typed Go struct keys that are inherently collision-free:

```go
type matchCacheKey struct {
    topicSelector string
    topic         string
}
```

The internal `TopicSelectorStoreCache` interface and sharded cache abstraction have also been removed in favor of a single typed otter cache.

Users should upgrade to version **0.22.0** or later.

### Workarounds

Disable the topic selector cache by setting `topic_selector_cache` to `-1` in the Caddyfile, or by passing a cache size of `0` when using the library directly. This eliminates the vulnerability at the cost of reduced performance.

## References
- https://github.com/dunglas/mercure/security/advisories/GHSA-hwr4-mq23-wcv5
- https://nvd.nist.gov/vuln/detail/CVE-2026-39972
- https://github.com/dunglas/mercure/commit/4964a69be904fd61e35b5f1e691271663b6fdd64
- https://github.com/dunglas/mercure
- https://github.com/dunglas/mercure/releases/tag/v0.22.0
