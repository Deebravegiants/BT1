# [H] @hulumi/policies bypasses policy packs with a forged Pulumi-URN logical name

## Summary
Severity: High
Advisory: GHSA-rhgj-6g2c-frmm
CVE: CVE-2026-48033
CWE: CWE-693
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:N/VI:H/VA:N/SC:H/SI:H/SA:N (CVSS_V4)
Published: 2026-06-10
Source: https://github.com/advisories/GHSA-rhgj-6g2c-frmm
Type: github-advisory

## Affected
- npm: `@hulumi/policies` — affected >=0 <1.4.0

## Details
**Affected:** `@hulumi/policies` `< 1.4.0` — **Fixed in:** `1.4.0` — **Severity:** High — **CWE-693 (Protection Mechanism Failure)**

#### Summary

Pulumi gives every cloud resource a structured URN that includes the resource's type chain (`hulumi:baseline:aws:SecureBucket$aws:s3/bucketV2:BucketV2`) and the _logical name_ the developer freely chose (anything after the final `::`). Several Hulumi policy rules used the URN to grant exemptions — for example, "if this raw bucket is a child of `SecureBucket`, skip the raw-bucket rule because the parent component handles hardening."

The bug: the rules looked for a substring like `hulumi:baseline:aws:SecureBucket$` _anywhere_ in the URN. That substring can also appear in the developer-controlled logical-name portion. A developer (or compromised PR) could simply name a raw resource so its logical name carried the trusted substring, and every rule that used this check would treat the resource as if it were inside the trusted parent and skip its hardening check.

Codex reported this for `DEPLOY_GOV_1`; the same anti-pattern existed in five more packs (unreported but identically exploitable): AWS H4/H5 sibling lookups, GitHub H1, GitHub H2, Cloudflare `CF_DNS_1`, Cloudflare `CF_DNSSEC_1`, and (advisory-level) CIS v5 §2.1.1 + §2.1.5.

#### Impact

Consumers using `@hulumi/policies` could ship raw `aws:s3:Bucket`, `github:Repository`, `cloudflare:Zone`, `cloudflare:DnsRecord`, and similar resources that bypassed mandatory hardening checks by naming themselves with a trusted substring. Every affected rule appeared to pass while the resource had none of the expected defaults.

#### Patches

Upgrade to `@hulumi/policies@1.4.0`. A new shared helper at `packages/policies/src/urn.ts` parses Pulumi URNs structurally and only looks for the trusted parent-type token inside the URN's type-chain segment — never inside the developer-controlled logical name. All six prior call sites have been migrated to it.

#### Workarounds

None reliable — a local lint that rejects logical names containing `$` would catch the trivial form of the spoof but not crafted variants.

#### Resources

- [PR #178](https://github.com/kerberosmansour/hulumi/pull/178) (Cluster B); the URN-anchoring refactor and per-pack spoof-vector regression tests in `packages/policies/tests/`.

## References
- https://github.com/kerberosmansour/hulumi/security/advisories/GHSA-rhgj-6g2c-frmm
- https://github.com/kerberosmansour/hulumi/pull/178
- https://github.com/kerberosmansour/hulumi
