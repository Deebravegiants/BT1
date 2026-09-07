# [H] Parse Server has Regular Expression Denial of Service (ReDoS) via `$regex` query in LiveQuery

## Summary
Severity: High
Advisory: GHSA-mf3j-86qx-cq5j
CVE: CVE-2026-30925
CWE: CWE-1333
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-03-10
Source: https://github.com/advisories/GHSA-mf3j-86qx-cq5j
Type: github-advisory

## Affected
- npm: `parse-server` — affected >=9.0.0-alpha.1 <9.5.0-alpha.14
- npm: `parse-server` — affected >=0 <8.6.11

## Details
### Impact

A malicious client can subscribe to a LiveQuery with a crafted `$regex` pattern that causes catastrophic backtracking, blocking the Node.js event loop. This makes the entire Parse Server unresponsive, affecting all clients. Any Parse Server deployment with LiveQuery enabled is affected. The attacker only needs the application ID and JavaScript key, both of which are public in client-side apps.

This only affects LiveQuery subscription matching, which evaluates regex in JavaScript on the Node.js event loop. Normal REST and GraphQL queries are not affected because their regex is evaluated by the database engine.

### Patches

Regex evaluation in LiveQuery subscription matching now runs in an isolated VM context with a configurable timeout via a new Parse Server option `liveQuery.regexTimeout, with defaults 100 ms. A regex that exceeds the timeout is treated as non-matching.

The protection adds approximately 50 microseconds of overhead per regex evaluation. For most applications this is negligible, but it can add up if there is a very large number of LiveQuery subscriptions that use `$regex` on the same class. For example, 10,000 concurrent regex subscriptions would add approximately 500ms of processing time per object save event on that class. Set `liveQuery.regexTimeout: 0` to disable the protection and use native regex evaluation without overhead.

### Workarounds

Use the `beforeSubscribe` Cloud Code hook to reject any LiveQuery subscription that contains a `$regex` operator. Note that this also blocks the LiveQuery `startsWith`, `endsWith`, and `contains` query methods, as they use `$regex` internally.

```js
// Repeat for each class that is used with LiveQuery
Parse.Cloud.beforeSubscribe('MyClass', request => {
  const where = request.query._where || {};
  for (const value of Object.values(where)) {
    if (value?.$regex) {
      throw new Parse.Error(Parse.Error.OPERATION_FORBIDDEN, '$regex not allowed in LiveQuery subscriptions');
    }
  }
});
```

### References

- GitHub security advisory: https://github.com/parse-community/parse-server/security/advisories/GHSA-mf3j-86qx-cq5j
- Fix Parse Server 9: https://github.com/parse-community/parse-server/releases/tag/9.5.0-alpha.14
- Fix Parse Server 8: https://github.com/parse-community/parse-server/releases/tag/8.6.11

## References
- https://github.com/parse-community/parse-server/security/advisories/GHSA-mf3j-86qx-cq5j
- https://nvd.nist.gov/vuln/detail/CVE-2026-30925
- https://github.com/parse-community/parse-server
- https://github.com/parse-community/parse-server/releases/tag/8.6.11
- https://github.com/parse-community/parse-server/releases/tag/9.5.0-alpha.14
