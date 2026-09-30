# [M] jackson-databind: @JsonView bypassed for @JsonUnwrapped container properties on deserialization

## Summary
Severity: Medium
Advisory: GHSA-5gvw-p9qm-jgwh
CVE: CVE-2026-59889
CWE: CWE-863
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2026-07-21
Source: https://github.com/advisories/GHSA-5gvw-p9qm-jgwh
Type: github-advisory

## Affected
- Maven: `com.fasterxml.jackson.core:jackson-databind` — affected >=2.21.0 <2.21.5
- Maven: `tools.jackson.core:jackson-databind` — affected >=3.0.0 <3.1.5
- Maven: `com.fasterxml.jackson.core:jackson-databind` — affected >=2.18.0 <2.18.9
- Maven: `com.fasterxml.jackson.core:jackson-databind` — affected >=2.22.0 <2.22.1
- Maven: `tools.jackson.core:jackson-databind` — affected >=3.2.0 <3.2.1

## Details
## Summary
`UnwrappedPropertyHandler.processUnwrapped()` replays the buffered JSON for a `@JsonUnwrapped` property by iterating its properties and calling `prop.deserializeAndSet()` with **no `prop.visibleInView(ctxt.getActiveView())` guard** — the exact guard `processUnwrappedCreatorProperties()` received in the #5971 / GHSA-rcqc-6cw3-h962 fix, and the guard `BeanDeserializer.deserializeWithUnwrapped` applies to directly-matched properties. As a result, a property annotated with both `@JsonView(PrivilegedView.class)` and `@JsonUnwrapped` is written from attacker JSON even when deserializing under a more-restrictive active view.

**Correction to the original framing (runtime-verified):** the gap is NOT a per-field inner `@JsonView` (the unwrapped sub-object's own `BeanDeserializer` gates inner fields correctly). The unchecked gate is the **view of the unwrapped CONTAINER property**.

## Intent proof (runtime, 2.x HEAD 21dd70dd and 3.x HEAD 7a5939d6)
An `@JsonView(AdminView)` property that is NOT `@JsonUnwrapped` → `null` under `PublicView` (correctly gated). The identical property WITH `@JsonUnwrapped` → fully populated (bypass). The fix the creator path already received, not applied to the regular-property method.

## Impact — write-side mass-assignment / privilege escalation
`@JsonView` is commonly used as a write-side authorization guard: a public endpoint binds the body under `readerWithView(PublicView.class)` and groups privileged state in a nested object whose container property is `@JsonView(AdminView)`. When that property is `@JsonUnwrapped`, an untrusted caller mass-assigns it. PoC: a self-service registration where `AccountFlags{role,approved,creditBalance}` is `@JsonView(AdminView) @JsonUnwrapped`; attacker JSON `{role:ADMIN,approved:true,creditBalance:1000000}` under `PublicView` binds all three → approved admin with arbitrary balance. The failing gate is a WRITE gate, hence integrity-high (`C:N/I:H/A:N`); no worse than the C:L/I:L parent and arguably higher as `@JsonView`-as-write-guard is the exact use case #5971/#5969 defended.

## Affected
- `com.fasterxml.jackson.core:jackson-databind` 2.x: confirmed bypass at 21dd70dd (== released 2.21.4 / 2.22.0 line; includes the #5973 backport). `DEFAULT_VIEW_INCLUSION` default=true.
- `tools.jackson.core:jackson-databind` 3.x: confirmed bypass at HEAD 7a5939d6 (latest 3.x). `DEFAULT_VIEW_INCLUSION` default=false → the stock-config repro is the common shape where privileged inner fields are individually `@JsonView(PublicView)` and the developer relies on the container `@JsonView(AdminView)`; the 3.x PoC mass-assigns role/approved/creditBalance under PublicView. (The other simultaneous report's PoC was reportedly fixed on 3.x; this distinct container-property path is not.)

## Additive variants (runtime-confirmed both branches; all closed by the same one-line guard)
- nested `@JsonUnwrapped` (unwrapped-in-unwrapped) — recursive bypass.
- merge / `readerWithView(...).withValueToUpdate(...)` (PATCH/partial-update) — bypass; non-unwrapped merge control gates correctly.
- builder-based deserializer (`@JsonDeserialize(builder=...)`) — `BuilderBasedDeserializer` routes through the same `processUnwrapped`.
- Honest non-findings: read-side serialization correctly honors views (no leak); `@JsonAnySetter`+view and `@JsonTypeInfo`+`@JsonUnwrapped` are separate/unsupported behaviors, not this bug.

## Fix
Add `prop.visibleInView(ctxt.getActiveView())` (when `MapperFeature.DEFAULT_VIEW_INCLUSION`/active-view applies) to the `processUnwrapped()` property loop, mirroring `processUnwrappedCreatorProperties()`. One change closes the impact PoC + all three variants across `BeanDeserializer` and `BuilderBasedDeserializer`. Full runnable PoCs (2.x + 3.x) + variant harnesses available on request.

## References
- https://github.com/FasterXML/jackson-databind/security/advisories/GHSA-5gvw-p9qm-jgwh
- https://nvd.nist.gov/vuln/detail/CVE-2026-59889
- https://github.com/FasterXML/jackson-databind/issues/6060
- https://github.com/FasterXML/jackson-databind/pull/6056
- https://github.com/FasterXML/jackson-databind/commit/d627a8a86fcb062429282f79f3f256f181ed2c7b
- https://github.com/FasterXML/jackson-databind
