# [M] Apollo Router Unnamed "Subscription" operation results in Denial-of-Service

## Summary
Severity: Medium
Advisory: GHSA-w8vq-3hf9-xppx
CVE: CVE-2023-41317
CWE: CWE-755
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2023-09-07
Source: https://github.com/advisories/GHSA-w8vq-3hf9-xppx
Type: github-advisory

## Affected
- crates.io: `apollo-router` — affected >=1.28.0 <1.29.1

## Details
### Impact

This is a Denial-of-Service (DoS) type vulnerability which causes the Router to panic and terminate when GraphQL Subscriptions are enabled.  It can be triggered when **all of the following conditions are met**:

1. Running Apollo Router v1.28.0, v1.28.1 or v1.29.0 ("impacted versions"); **and**
2. The Supergraph schema provided to the Router (either via Apollo Uplink or explicitly via other configuration) **has a `subscription` type** with root-fields defined; **and**
3. The YAML configuration provided to the Router **has subscriptions enabled** (they are _disabled_ by default), either by setting `enabled: true` _or_ by setting a valid `mode` within the `subscriptions` object (as seen in [subscriptions' documentation](https://www.apollographql.com/docs/router/executing-operations/subscription-support/#router-setup)); **and**
4. An [anonymous](https://spec.graphql.org/draft/#sec-Anonymous-Operation-Definitions) (i.e., un-named) `subscription` operation (e.g., `subscription { ... }`) is received by the Router

If **all four** of these criteria are met, the impacted versions will panic and terminate.  There is no data-privacy risk or sensitive-information exposure aspect to this vulnerability.

Depending on the environment in which impacted versions are running and the high-availability characteristics of that environment, a single Router's termination may result in limited or reduced availability or other knock-on effects which are deployment-specific (e.g., depending on if there are multiple instances, auto-restart policies, etc.)

### Discovery

This vulnerability was discovered by an internal Apollo team.  We have no reports or evidence to support that that has been exploited outside of our own testing, research and follow-up.

Our public security policy can be reviewed at https://github.com/apollographql/router/security/policy and we consider the security of our projects a top priority.  Please review the linked policy for more details.

### Patches

This is fixed in [Apollo Router v1.29.1](https://github.com/apollographql/router/releases/tag/v1.29.1), which is available on:

- [GitHub Releases](https://github.com/apollographql/router/releases) as `v1.29.1`
- [GitHub Packages Container Registry](https://github.com/apollographql/router/pkgs/container/router) as `v1.29.1`
- [Helm Chart Repository](https://github.com/apollographql/router/pkgs/container/helm-charts%2Frouter) as `1.29.1` (without the `v`)

We recommend all users running the impacted configuration above to update to a patched version of the Router immediately.  Router v1.29.1 should be a very simple upgrade from any impacted version. 

### Workarounds

Updating to v1.29.1 should be a clear and simple upgrade path for those running impacted versions.  However, if Subscriptions are **not** necessary for your Graph – but are enabled via configuration — then disabling subscriptions is another option to mitigate the risk.

### For more information

If you have any questions or comments about this advisory:

* Open an issue in [the `router` repository](https://github.com/apollographql/router)
* Email us at `security` `[at]` `apollographql` `[dot]` `com`

## References
- https://github.com/apollographql/router/security/advisories/GHSA-w8vq-3hf9-xppx
- https://nvd.nist.gov/vuln/detail/CVE-2023-41317
- https://github.com/apollographql/router/commit/b295c103dd86c57c848397d32e8094edfa8502aa
- https://github.com/apollographql/router
- https://github.com/apollographql/router/releases/tag/v1.29.1
