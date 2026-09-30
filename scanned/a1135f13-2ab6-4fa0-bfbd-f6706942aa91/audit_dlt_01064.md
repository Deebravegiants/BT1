# [H] libp2p-rendezvous: Unbounded rendezvous DISCOVER cookies enable remote memory exhaustion

## Summary
Severity: High
Chain: libp2p-rendezvous
Component: libp2p-rendezvous
CVE: CVE-2026-35457
CWE: Allocation of Resources Without Limits or Throttling
Published: 2026-04-04
Source: https://github.com/advisories/GHSA-v5hw-cv9c-rpg7
Type: github-advisory

## Details
### Summary
The rendezvous server stores pagination cookies without bounds. An unauthenticated peer can repeatedly issue `DISCOVER` requests and force unbounded memory growth.

### Details

Pagination state is stored in:

```rs
HashMap<Cookie, HashSet<RegistrationId>>
```

On `Message::Discover`:

```
remote peer
→ DISCOVER
→ handle_request
→ registrations.get(...)
→ new cookie generated
→ cookie inserted into Registrations::cookies
```

There is **no upper bound or eviction policy**, so repeated DISCOVER requests grow this map indefinitely.


### PoC
A reproduction test and minimal harness will be provided in a private fork in a follow-up comment.

### Impact

**Remote state amplification leading to memory exhaustion.**


Properties:

- etwork reachable
- no authentication required
- low attack complexity
- protocol-compliant traffic

Impacts rendezvous nodes exposed to untrusted peers.
---

### Possible Fixes

1. **Global cap + eviction**

Bound cookie storage (`MAX_COOKIES_TRACKED`) with FIFO/expiry aware eviction.  
Tradeoff: attacker can churn cookies and evict legitimate pagination state.

2. **Stateless cookies**

Encode pagination state in authenticated cookies instead of storing server-side state.  
Tradeoff: more complex implementation.

3. **Rate limiting / per-peer quotas**

Limit cookie creation per peer.  
Tradeoff: requires peer tracking.
