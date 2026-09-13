# [H] @hulumi/baseline: AccountFoundation audit-delivery S3 bucket could be silently weakened

## Summary
Severity: High
Advisory: GHSA-2mxr-p26x-mj73
CVE: CVE-2026-48035
CWE: CWE-1059
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:N/VI:H/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-06-10
Source: https://github.com/advisories/GHSA-2mxr-p26x-mj73
Type: github-advisory

## Affected
- npm: `@hulumi/baseline` — affected >=0 <1.4.0

## Details
**Affected:** `@hulumi/baseline` `< 1.4.0` — **Fixed in:** `1.4.0` — **Severity:** High — **CWE-1059 (Insufficient Technical Documentation / Behavioral Inconsistency)**

#### Summary

The S3 bucket that `AccountFoundation` creates to receive CloudTrail and AWS Config audit logs is meant to be tamper-resistant — if someone with delete access can erase from it, the forensic trail is gone. There were three independent ways the protection could be silently weakened:

1. **No Write-Once-Read-Many on the startup-hardened audit bucket.** The startup-hardened tier hard-coded `objectLock: false` on the audit bucket. (The reason was real — bucket-wide Object Lock blocks an AWS Config write-then-delete probe — but the fix was a sledgehammer that disabled WORM for all objects, not just the probe key.)
2. **`forceDestroy` was forwarded to the audit bucket.** Nothing prevented a downstream stack from setting `logBucketForceDestroy: true`, which made `pulumi destroy` purge every audit-log object on teardown.
3. **Sandbox tier dropped everything.** Sandbox-tier `AccountFoundation` created its audit bucket with `tier: "sandbox"`, which skipped Object Lock, server access logging, AND the CloudTrail-Lake `EventDataStore` (the independent immutable mirror) — leaving sandbox accounts with no audit immutability at all.

#### Impact

Consumers using `AccountFoundation` could ship an AWS account whose CloudTrail / Config audit logs were deletable by any S3-delete-capable principal — while believing the startup-hardened tier guaranteed tamper-resistance. Sandbox-tier deployments had no audit immutability at all (defects 1 and 3 compounded).

#### Patches

Upgrade to `@hulumi/baseline@1.4.0`. A single invariant in `SecureBucket` now fires whenever the bucket actually backs CloudTrail/Config delivery (i.e. `awsServiceLogDelivery.cloudTrail === true || .config === true`):

- refuses `forceDestroy: true` on the startup-hardened tier;
- emits the CloudTrail-Lake `EventDataStore` regardless of parent tier (so sandbox accounts regain immutable audit capture);
- adds a deny-`s3:DeleteObject*` bucket-policy statement scoped to the CloudTrail and Config history/snapshot prefixes (a retention floor on the audit objects). The deny excludes the AWS Config `ConfigWritabilityCheckFile` probe key so Config's write-then-delete still works, which is why bucket-wide Object Lock is intentionally NOT re-enabled.

#### Workarounds

Replicating audit logs out-of-account to an Object-Locked archive bucket partially mitigates while you upgrade.

#### Resources

- [PR #178](https://github.com/kerberosmansour/hulumi/pull/178) (Cluster C); see CHANGELOG `### Migration` for the `forceDestroy` behaviour change.

## References
- https://github.com/kerberosmansour/hulumi/security/advisories/GHSA-2mxr-p26x-mj73
- https://github.com/kerberosmansour/hulumi/pull/178
- https://github.com/kerberosmansour/hulumi
