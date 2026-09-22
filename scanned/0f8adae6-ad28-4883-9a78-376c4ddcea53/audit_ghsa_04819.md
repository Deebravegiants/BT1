# [M] @hulumi/baseline: AccountFoundation reuse paths silently downgrade GuardDuty / Security Hub posture

## Summary
Severity: Medium
Advisory: GHSA-cj8g-prcm-mfg5
CVE: CVE-2026-48037
CWE: CWE-693
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:N/VI:L/VA:N/SC:L/SI:H/SA:N (CVSS_V4)
Published: 2026-06-10
Source: https://github.com/advisories/GHSA-cj8g-prcm-mfg5
Type: github-advisory

## Affected
- npm: `@hulumi/baseline` — affected >=0 <1.4.0

## Details
**Affected:** `@hulumi/baseline` `< 1.4.0` — **Fixed in:** `1.4.0` — **Severity:** Medium — **CWE-693 (Protection Mechanism Failure)**

#### Summary

`AccountFoundation` can either create AWS detective services (GuardDuty for threat detection, Security Hub for compliance dashboards) or reuse pre-existing ones via opt-in flags. The reuse paths just imported the existing resources and reported success — they never checked whether the existing services were actually doing their job.

1. **GuardDuty reuse.** If the existing detector was suspended, or set to the slower 6-hour publishing cadence instead of the baseline 15-minute one, or otherwise misconfigured — Hulumi never noticed. The deployment succeeded with a misleadingly-positive `guardDutyDetectorId` output as if the baseline were active.
2. **Security Hub reuse.** Although the account import was read-only, Hulumi unconditionally created the CIS / NIST `StandardsSubscription` resources with default delete behaviour. Pulumi then treated those subscriptions as its own — a later `pulumi destroy` of the stack would call `BatchDisableStandards`, unsubscribing the account from CIS / NIST compliance monitoring even on accounts that had those subscriptions before Hulumi ever ran.

#### Impact

Consumers using `AccountFoundation`'s reuse mode could:

- ship deployments that appeared to enable a detective baseline but actually weren't (case 1), or
- accidentally turn off CIS / NIST compliance monitoring on an existing account just by destroying a Hulumi stack (case 2 — no malicious intent needed; a normal stack teardown was enough).

#### Patches

Upgrade to `@hulumi/baseline@1.4.0`.

- GuardDuty reuse now asserts the imported detector is `ENABLED` with `findingPublishingFrequency: FIFTEEN_MINUTES`. Wrong posture fails the deploy at preview time.
- Security Hub reuse creates the CIS / NIST `StandardsSubscription` resources with `retainOnDelete: true`, so destroying a reused stack no longer unsubscribes the account.

Net-new (non-reuse) deployments are unchanged.

#### Workarounds

Don't reuse pre-existing detective services with `AccountFoundation` before upgrading. If reuse is unavoidable, manually verify detector posture out-of-band.

#### Resources

- [PR #178](https://github.com/kerberosmansour/hulumi/pull/178) (Cluster G); regression tests in
  `packages/baseline/tests/guardduty-reuse-posture.test.ts` and
  `packages/baseline/tests/securityhub-reuse-retain.test.ts`.

## References
- https://github.com/kerberosmansour/hulumi/security/advisories/GHSA-cj8g-prcm-mfg5
- https://github.com/kerberosmansour/hulumi/pull/178
- https://github.com/kerberosmansour/hulumi
