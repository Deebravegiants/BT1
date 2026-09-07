# [H] @hulumi/drift: Drift classifier fails open on adapter errors and over-promotes Mixed verdicts

## Summary
Severity: High
Advisory: GHSA-32g3-35g9-wc9g
CVE: CVE-2026-48036
CWE: CWE-755
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:P/VC:N/VI:H/VA:L/SC:N/SI:H/SA:L (CVSS_V4)
Published: 2026-06-10
Source: https://github.com/advisories/GHSA-32g3-35g9-wc9g
Type: github-advisory

## Affected
- npm: `@hulumi/drift` — affected >=0 <1.4.0

## Details
**Affected:** `@hulumi/drift` `< 1.4.0` — **Fixed in:** `1.4.0` — **Severity:** Medium — **CWE-755 (Improper Handling of Exceptional Conditions)**

#### Summary

`@hulumi/drift` runs four adapters that each ask a different question about whether a resource has drifted (Pulumi-state diff, provider-version change, CloudTrail event, etc.). A classifier combines the adapters' answers into a verdict like `None / none`, `ConsoleBreakGlass / high`, or `Mixed / high`, and caches the verdict for 6 hours by default.

Two related bugs from one root cause — the classifier only read each adapter's `detected: true/false` field and ignored whether the adapter itself succeeded:

1. **Cached "all clear" on adapter failure.** When an adapter failed (e.g. transient network error from the Automation API), the classifier read `detected: false`, concluded "no drift", and cached the verdict as `None / none` for 6 hours. A single transient failure could mask real console-break-glass mutations for the rest of the window.
2. **Mixed verdicts without real evidence.** The `Mixed / high` and `ConsoleBreakGlass / high` verdicts (incident severity) could fire on the "the CloudTrail probe round-tripped successfully" signal rather than actual evidence that anything had been changed via the console. Normal provider-API churn could end up falsely escalated to incident severity.

#### Impact

Consumers running drift detection in CI / cron could see transient adapter failures silently cached as "all clear" — masking real attacks for up to six hours — or see ordinary provider-version churn falsely promoted to incident severity. Either way, the verdict source was unreliable for downstream incident workflows that gate on it.

#### Patches

Upgrade to `@hulumi/drift@1.4.0`. Classifier-only fix (the TLA+-verified 6-row verdict matrix is byte-identical):

- adapter failures now fail closed to `Unknown / low`, and degraded verdicts are not written to the cache;
- the `Mixed` / `ConsoleBreakGlass` promotion now requires real CloudTrail event evidence rather than probe liveness.

#### Workarounds

Setting `options.minConfidence: "medium"` on the classifier call prevents the degraded `None / none` from being cached (it doesn't meet the threshold), partially mitigating case (1). No workaround for case (2).

#### Resources

- [PR #178](https://github.com/kerberosmansour/hulumi/pull/178) (Cluster D); regression tests in `packages/drift/tests/classifier-fail-closed.test.ts`.

## References
- https://github.com/kerberosmansour/hulumi/security/advisories/GHSA-32g3-35g9-wc9g
- https://github.com/kerberosmansour/hulumi/pull/178
- https://github.com/kerberosmansour/hulumi
