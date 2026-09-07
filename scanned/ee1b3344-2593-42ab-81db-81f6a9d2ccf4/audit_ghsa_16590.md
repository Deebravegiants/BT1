# [C] Apollo Router vulnerable to Critical Regression In Query Plan Cache

## Summary
Severity: Critical
Advisory: GHSA-q9p4-hw9m-fj2v
CVE: CVE-2024-32971
CWE: CWE-440
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2024-05-02
Source: https://github.com/advisories/GHSA-q9p4-hw9m-fj2v
Type: github-advisory

## Affected
- crates.io: `apollo-router` — affected >=1.44.0 <1.45.1

## Details
### Impact
Any instance of Apollo Router 1.44.0 or 1.45.0 that is using Distributed Query Plan Caching is impacted. These versions were released on 2024-04-12 and 2024-04-22 respectively.

The affected versions of Apollo Router contain a bug that could lead to unexpected operations being executed, which can result in unintended data or effects. This only affects Router instances configured to use distributed query plan caching. Router versions other than the ones listed above, and all Router deployments that are not using distributed query plan caching, are unaffected by this defect.

If you are using the affected versions, you can check your router’s configuration YAML to verify if you are impacted:


```yaml
supergraph:
  query_planning:
    cache:
      # Look for this config below
      redis:
        urls: ["redis://..."]
```
A full reference on the[ Distributed Query Plan Caching feature is available here.](https://www.apollographql.com/docs/router/configuration/distributed-caching/#distributed-query-plan-caching)

### Impact detail
The root cause of this defect is a bug in Apollo Router’s cache retrieval logic: When this defect is present and distributed query planning caching is enabled, asking the Router to execute an operation (whether it is a query, a mutation, or a subscription) may result in an unexpected variation of that operation being executed or the generation of unexpected errors.  

The issue stems from inadvertently executing a modified version of a previously executed operation, whose query plan is stored in the underlying cache (specifically, Redis). Depending on the type of the operation, the result may vary.  For a query, results may be fetched that don’t match what was requested (e.g., rather than running `fetchUsers(type: ENTERPRISE)` the Router may run `fetchUsers(type: TRIAL)`.  For a mutation, this may result in incorrect mutations being sent to underlying subgraph servers (e.g., rather than sending `deleteUser(id: 10)` to a subgraph, the Router may run `deleteUser(id: 12)`.

### Patches
Apollo Router 1.45.1

If you are using distributed query plan caching, please either upgrade to version 1.45.1 or above or downgrade to version 1.43.2 of the Apollo Router. We do not recommend Apollo Router versions 1.44.0 or 1.45.0 for use and have withdrawn these releases. If you use impacted versions in production, we recommend that you migrate away immediately by redeploying to an unaffected Router version. For non-production use cases, we recommend you migrate at your earliest convenience.

### Workarounds
If you cannot upgrade or downgrade, you can disable distributed query plan caching by removing the `supergraph.query_planning.cache.redis.urls` configuration. Please note that when distributed query plan caching is disabled, each Router instance will maintain its own in-memory query plan cache. This may increase resource utilization for each Router instance and could increase cold-start times as each Router instance builds its query plan cache.

### References
[Apollo Router 1.45.1 Release Notes](https://github.com/apollographql/router/releases/tag/v1.45.1)

## References
- https://github.com/apollographql/router/security/advisories/GHSA-q9p4-hw9m-fj2v
- https://nvd.nist.gov/vuln/detail/CVE-2024-32971
- https://github.com/apollographql/router/commit/ff9f666598cd17661880fe7fc6e9c9611316e529
- https://github.com/apollographql/router
- https://github.com/apollographql/router/releases/tag/v1.45.1
- https://www.apollographql.com/docs/router/configuration/distributed-caching/#distributed-query-plan-caching
