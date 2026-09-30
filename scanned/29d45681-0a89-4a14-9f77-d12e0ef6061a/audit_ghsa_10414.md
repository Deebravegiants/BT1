# [H] Meridian: Multiple defense-in-depth gaps (collection/depth caps, telemetry, retry, fan-out)

## Summary
Severity: High
Advisory: GHSA-f5v8-v6q3-q4h6
CWE: CWE-1325, CWE-209, CWE-400, CWE-532, CWE-665, CWE-674, CWE-770
Ecosystem: NuGet
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-04-16
Source: https://github.com/advisories/GHSA-f5v8-v6q3-q4h6
Type: github-advisory

## Affected
- NuGet: `Meridian.Mapping` — affected >=2.0.0 <2.1.1
- NuGet: `Meridian.Mediator` — affected >=2.0.0 <2.1.1

## Details
## Summary

Meridian v2.1.0 (`Meridian.Mapping` and `Meridian.Mediator`) shipped with nine defense-in-depth gaps reachable through its public APIs. Two are HIGH severity — the advertised `DefaultMaxCollectionItems` and `DefaultMaxDepth` safety caps are silently bypassed on the `IMapper.Map(source, destination)` overload and anywhere `.UseDestinationValue()` is configured on a collection-typed property. Four are MEDIUM (constructor invariant bypass, OpenTelemetry stack-trace info disclosure, retry amplification, notification fan-out amplification). Three are LOW (exception message disclosure, dictionary duplicate-key echo, static mediator cache growth under closed-generic types).

All nine are patched in **v2.1.1**. Upgrade is a drop-in NuGet bump; see the v2.1.1 CHANGELOG for the four behavioural changes (constructor selection, OTel default, publisher fan-out cap, retry caps).

## Severity Matrix

| # | Severity | CWE | Finding | Fix |
|---|---|---|---|---|
| 1 | **HIGH** | CWE-770 | `MappingEngine.TryMapCollectionOntoExisting` enumerated the source without enforcing `DefaultMaxCollectionItems`. Reachable via `Mapper.Map<TSrc,TDst>(src, dst)` and any `.ForMember(..., o => o.UseDestinationValue())` on a collection member through a plain `Map(src)` call. | Shared cap enforcement helper between `MapCollection` and `TryMapCollectionOntoExisting`. |
| 2 | **HIGH** | CWE-674 | Collection-item recursion in the existing-destination path did not increment `ResolutionContext.Depth`, so self-referential collection graphs could reach stack overflow before `DefaultMaxDepth` fired. | Depth increments at every collection-item boundary. |
| 3 | MEDIUM | CWE-665 | `ObjectCreator.CreateWithConstructorMapping` always invoked the widest public constructor, silently filling unresolved parameters with `default(T)` and bypassing narrower-ctor invariants. | Widest-ctor selection now requires every parameter to be bound via explicit ctor mapping, source-name match, or a C# optional default. |
| 4 | MEDIUM | CWE-532 | `Mediator.MarkActivityFailure` emitted the full `ex.ToString()` (stack + inner chain) to the OpenTelemetry `exception.stacktrace` activity tag by default, leaking context to any shared trace sink. | Gated on `MediatorTelemetryOptions.RecordExceptionStackTrace` — opt-in, default `false`. |
| 5 | MEDIUM | CWE-400 | `RetryBehavior` retried every exception type with unbounded `MaxRetries`; the exponential-backoff delay overflowed `TimeSpan` at ~30 attempts. No cancellation exclusion. | Server-side `MaxRetriesCap = 10`, `MaxBackoff = 5 min`, `OperationCanceledException` short-circuit, recommended `RetryPolicy.TransientOnly` helper. |
| 6 | MEDIUM | CWE-400 | `TaskWhenAllPublisher` started every registered handler concurrently with no bound on fan-out. | New constructor parameter `maxDegreeOfParallelism` (default 16; `-1` restores legacy unbounded). |
| 7 | LOW | CWE-209 | Public mapping exceptions leaked `FullName` of source/destination types and concatenated inner exception messages into top-level property-mapping errors. | Scrubbed to type `Name`; inner details only via `InnerException` chain. |
| 8 | LOW | CWE-209 | Dictionary materialization threw `ArgumentException` on duplicate keys, echoing the attacker-supplied key's `.ToString()`. | Last-write-wins indexer semantics. |
| 9 | LOW | CWE-1325 | Static mediator handler caches grow monotonically under closed-generic request types. **Doc-only mitigation**; no code change — consumers must not allow attacker-controlled runtime type materialization to reach `Send`, `Publish`, or `CreateStream`. | Documented in `docs/security-model.md`. |

## Exploitation

**Finding 1 / 2 (headline):** A consumer that maps user-supplied collection payloads onto an existing destination list via `mapper.Map(userCollection, existingList)` — a documented and commonly used AutoMapper-style idiom — processes the full attacker-supplied collection with no size cap and no depth cap. An attacker sending a single request with a large (or self-referential) collection payload can block the worker thread for seconds and exhaust the managed heap or the call stack. Equivalent exposure through `.UseDestinationValue()` on a collection-typed destination member, reachable via a plain `Map(src)` call whose destination type default-initializes that member.

**Finding 3:** A destination type with multiple public constructors that differ only in their parameter-binding invariants (e.g., `new UserAccount(string name, Email email)` enforcing a non-default `Email`) could be instantiated with the narrower ctor's invariants silently bypassed if any source field was absent — the widest ctor was always picked, with unbound parameters replaced by `default(T)`.

**Findings 4 / 5 / 6:** Amplification / information-disclosure vectors described in the matrix above. Each requires moderate integration context (telemetry sink trust, handler count, retry policy) to weaponize, but each is reachable through public APIs without authentication.

## Patches

- `Meridian.Mapping` **2.1.1** (published 2026-04-16)
- `Meridian.Mediator` **2.1.1** (published 2026-04-16)

Verified via:
- GitHub Release assets at <https://github.com/UmutKorkmaz/meridian/releases/tag/v2.1.1>
- Sigstore attestation (`actions/attest-build-provenance@v2` → `gh attestation verify` green on both `.nupkg` from the GitHub Release)
- NuGet.org indexed both packages within the release workflow run

## Workarounds

Users who cannot upgrade immediately may:
1. Avoid `mapper.Map(src, dst)` and `.UseDestinationValue()` on collection-typed destination members.
2. Wrap input collection deserialization with an explicit size limit before handing the payload to Meridian.
3. Register `TaskWhenAllPublisher` with `maxDegreeOfParallelism` ≤ 16 manually (v2.1.1+ only).
4. Disable OpenTelemetry `exception.stacktrace` tag emission at the trace exporter level if your trace sink is less trusted than your application.

These are defense-in-depth; the only complete mitigation is upgrading to 2.1.1.

## Supported Versions

As of this advisory the supported security branch is **2.1.x**. The 2.0.x line (published 2026-04-15) is not receiving the Phase 1 safety-defaults infrastructure needed to carry the HIGH-severity fixes, so 2.0.x is deprecated in favor of 2.1.x. See `SECURITY.md` for the updated supported-versions table.

## Credits

- UmutKorkmaz (reporter and maintainer)

## References

- v2.1.1 CHANGELOG section: <https://github.com/UmutKorkmaz/meridian/blob/main/CHANGELOG.md#211---2026-04-16>
- `docs/security-model.md` threat model: <https://github.com/UmutKorkmaz/meridian/blob/main/docs/security-model.md>
- `SECURITY.md` disclosure policy: <https://github.com/UmutKorkmaz/meridian/blob/main/SECURITY.md>
- AutoMapper CVE-2026-32933 (motivating precedent for Meridian's safety-defaults)

## References
- https://github.com/UmutKorkmaz/meridian/security/advisories/GHSA-f5v8-v6q3-q4h6
- https://github.com/UmutKorkmaz/meridian
- https://github.com/UmutKorkmaz/meridian/blob/main/CHANGELOG.md#211---2026-04-16
- https://github.com/UmutKorkmaz/meridian/releases/tag/v2.1.1
