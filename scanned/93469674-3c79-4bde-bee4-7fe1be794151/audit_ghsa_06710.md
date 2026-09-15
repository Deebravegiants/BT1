# [H] OmniFaces: Forged combined-resource IDs and related output/push boundaries

## Summary
Severity: High
Advisory: GHSA-fp43-vj7g-pg92
CWE: CWE-345, CWE-770, CWE-79, CWE-862
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-07-24
Source: https://github.com/advisories/GHSA-fp43-vj7g-pg92
Type: github-advisory

## Affected
- Maven: `org.omnifaces:omnifaces` — affected >=0 <1.14.3
- Maven: `org.omnifaces:omnifaces` — affected >=2.0.0 <2.7.33
- Maven: `org.omnifaces:omnifaces` — affected >=3.0.0 <3.14.23
- Maven: `org.omnifaces:omnifaces` — affected >=4.0.0 <4.7.12
- Maven: `org.omnifaces:omnifaces` — affected >=5.0.0 <5.4.2

## Details
## 1. Forged combined-resource IDs
`CombinedResourceInfo` accepts a path-derived ID without an authenticity check,
inflates it without an output limit, converts it to attacker-selected resource
identifiers, and retains unique IDs in an unbounded static cache. In bounded
tests, 20,754 encoded bytes inflated to 16,000,000 characters (about 770:1;
about 49 MB observed heap delta), and 200 unique IDs added 200 permanent cache
entries. A legitimately shaped short ID remained about 1:1, while malformed
input was rejected; the missing distinction is between a server-issued ID and
an attacker-minted but structurally valid ID.

The minimal application also confirmed three sink tails from the same forged-ID
root:

- A wildcard CDN mapping performed a server-side fetch and relayed the exact
  loopback-canary body. This requires the documented combined-resource and
  wildcard-CDN configuration.
- A forged inner `.xhtml` resource bypassed the excluded-resource boundary and
  returned its raw content.
- A forged `omnifaces.graphic` inner resource plus a canary `Host` header caused
  an outbound GET to that host. This result is blind and deployment-dependent;
  I am not claiming arbitrary-scheme or arbitrary-destination SSRF.

These behaviors reproduce after the fix for CVE-2026-41883 /
GHSA-vp6r-9m58-5xv8. That advisory concerned EL evaluation order in the wildcard
CDN path. This report has a different root: unsigned combined IDs and missing
decode/cache bounds, with separately demonstrated residual sink behavior.

## 2. Source-map cache 

With the documented optional source-map handler above a synthetic resource
handler, 40 unique missing combined-resource requests grew the process-wide
source-map cache from 13 to 92 entries. It has no size or eviction bound. This
has a separate cache, configuration prerequisite, and fix from family 1.

## 3. HashParam callback output

A URL-fragment value containing a single-quote JavaScript payload was stored by
`o:hashParam` and later written unescaped into the Ajax callback script. On the
follow-up Ajax render, real Chrome executed the canary
`window.__omniXss=1337`. This requires a page using `o:hashParam` and the
follow-up Ajax render.

## 4. Session/view push-channel replay 

A fresh WebSocket client with no HTTP cookie connected using a victim's
session-scoped channel ID and received the victim's subsequent push. The code
checks application-wide ID existence but does not bind the handshake to the
current HTTP session, despite the documented current-session guarantee. The
UUID remains an unguessable bearer-token prerequisite; this is replay after
token exposure, not brute force.

## 5. Push idle-connection and fanout behavior 

Twelve independent clients joined one application-scoped channel and all 12
received the same push. Current code sets every accepted session's maximum idle
timeout to zero, retains sessions in an unbounded per-channel queue, and walks
the full queue on each push. I am reporting the demonstrated mechanism as a
bounded design weakness: container connection limits remain an outer bound,
and I am not claiming unbounded heap growth from the 12-client test.

## Intentionally excluded leads

- A duplicate-Range response-amplification lead was disproved. Twenty-four
  ranges produced only one response body because the stream wrapper closes
  after the first range. I am not reporting it as a security issue.
- The older `Servlets.facesRedirect` XML issue is fixed on the current branch.
  I am not reporting it as a new current-upstream issue.

## Expected invariants

- Only server-issued combined IDs should be accepted; decoding and caches
  should be bounded; excluded resources and dynamic handlers should not become
  attacker-selected inner resources.
- Dynamic URLs should not derive an outbound destination from an untrusted
  `Host` header.
- Source-map lookups should not create unbounded process-lifetime state.
- `HashParam` values must be escaped for a JavaScript string inside an XML
  CDATA callback.
- Session/view push subscriptions should be bound to the owning HTTP session or
  authenticated principal; idle limits and per-channel caps should remain
  operator-controllable.

## Suggested fixes and available evidence

- Authenticate generated combined IDs with a per-deployment secret, cap
  inflated output, bound the combined cache, and avoid caching failed loads.
- Require an existing/registered inner resource before wildcard remapping and
  reject excluded resource types at serve time.
- Derive dynamic-resource origins from trusted configuration rather than the
  request `Host` value.
- Bound or evict the source-map cache.
- Apply JavaScript-string plus CDATA-safe encoding to `HashParam` callback
  values.
- Capture and verify HTTP-session or principal ownership during the WebSocket
  handshake; retain a finite idle timeout and configurable per-channel limits.

Daniel Birtwhistle

## References
- https://github.com/omnifaces/omnifaces/security/advisories/GHSA-fp43-vj7g-pg92
- https://github.com/omnifaces/omnifaces/commit/59d6c5188c39418546fe500d05036645987a77d1
- https://github.com/omnifaces/omnifaces/commit/a52b92461cf39d983f51ce8724fe7e6b944073e4
- https://github.com/omnifaces/omnifaces/commit/aa42da361821ddfbb85b126564e71587347d2786
- https://github.com/omnifaces/omnifaces/commit/c43eef01174a4dc09cec44eff553ff6284150af7
- https://github.com/omnifaces/omnifaces/commit/d5cae243c4692555efaa4ba774e0f8f60e3f4db5
- https://github.com/omnifaces/omnifaces
