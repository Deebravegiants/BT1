# [H] @hulumi/policies has a HULUMI-H5 bypass via decoy sibling resources targeting a different bucket

## Summary
Severity: High
Advisory: GHSA-9vc9-4jv3-rf86
CVE: CVE-2026-48034
CWE: CWE-284
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:N/VI:H/VA:N/SC:H/SI:H/SA:L (CVSS_V4)
Published: 2026-06-10
Source: https://github.com/advisories/GHSA-9vc9-4jv3-rf86
Type: github-advisory

## Affected
- npm: `@hulumi/policies` — affected >=0 <1.4.0

## Details
**Affected:** `@hulumi/policies` `< 1.4.0` — **Fixed in:** `1.4.0` — **Severity:** High — **CWE-284 (Improper Access Control)**

#### Summary

HULUMI-H1 forbids raw `aws:s3:Bucket` outside of Hulumi's `SecureBucket` component, with one exemption: a raw bucket that's a child of a `SecureBucket` is allowed because the component is responsible for the hardening. HULUMI-H5 is the defence-in-depth check that closes the H1 exemption — for any raw bucket claiming it, H5 verifies the five hardening sibling resources a real `SecureBucket` always emits (public-access block, SSE-KMS, ownership controls, versioning, TLS-only bucket policy) are actually present.

The bug: H5 only checked the siblings' _types_. It never verified that those siblings actually applied to the bucket being exempted. A consumer (or compromised PR) could pair an unhardened raw bucket with five hardening sibling resources whose `bucket` property pointed at a _completely different_ bucket, and H5 would report no violation while the actual bucket shipped with zero hardened defaults.

#### Impact

Consumers using `HulumiHardeningPack` could ship a raw S3 bucket with no public-access block, no SSE-KMS, no ownership controls, no versioning, and no TLS-only bucket policy — while the policy pack reported the stack as compliant.

#### Patches

Upgrade to `@hulumi/policies@1.4.0`. The H5 sibling check now requires both (a) the sibling to share the same parent `SecureBucket` instance via the anchored URN helper from GHSA-2, AND (b) the sibling's `bucket` property — or, for the bucket policy, its `Resource` ARN list — to reference the exempted bucket explicitly. Five decoy siblings pointing at a different bucket no longer count.

#### Workarounds

None — the exemption itself is the mechanism, so the value-binding check is the only fix.

#### Resources

- [PR #178](https://github.com/kerberosmansour/hulumi/pull/178) (Cluster B); decoy-sibling regression cases in `packages/policies/tests/hulumi-hardening-pack.test.ts`. Supersedes [PR #175](https://github.com/kerberosmansour/hulumi/pull/175), which had addressed the value-binding half but on a stale base.

## References
- https://github.com/kerberosmansour/hulumi/security/advisories/GHSA-9vc9-4jv3-rf86
- https://github.com/kerberosmansour/hulumi/pull/175
- https://github.com/kerberosmansour/hulumi/pull/178
- https://github.com/kerberosmansour/hulumi
