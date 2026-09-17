# [H] Zod denial of service vulnerability during email validation

## Summary
Severity: High
Advisory: GHSA-mvrp-3cvx-c325
CWE: CWE-1333
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2023-10-04
Source: https://github.com/advisories/GHSA-mvrp-3cvx-c325
Type: github-advisory

## Affected
- npm: `express-zod-api` — affected >=0 <10.0.0-beta1

## Details
### Impact

API servers running `express-zod-api` having:

- version of `express-zod-api` below `10.0.0-beta1`,
- and using the following (or similar) validation schema in its implementation: `z.string().email()`,

are vulnerable to a DoS attack due to: 

- Inefficient Regular Expression Complexity in `zod` versions up to `3.22.2`,
- depending on `zod`.

### Patches

The patched version of `zod` fixing the vulnerability is `3.22.3`.

However, it's highly recommended to upgrade `express-zod-api` to at least version `10.0.0`, which does not depend on `zod` strictly and directly, but requires its installation as a peer dependency instead, enabling you to install the patched `zod` version yourself.

### Workarounds

When it's not possible to upgrade your dependencies, consider the following replacement in your implementation:

```diff
- z.string().email()
+ z.string().regex(
+   /^(?!\.)(?!.*\.\.)([A-Z0-9_+-\.]*)[A-Z0-9_+-]@([A-Z0-9][A-Z0-9\-]*\.)+[A-Z]{2,}$/i
+ )
```

This regular expression is taken from the suggested patch of `zod`.

### References

- Original issue: https://github.com/colinhacks/zod/issues/2609
- The patch: https://github.com/colinhacks/zod/pull/2824
- Entry in database: https://nvd.nist.gov/vuln/detail/CVE-2023-4316
- Enumeration: https://cwe.mitre.org/data/definitions/1333.html
- Parent advisory: https://github.com/advisories/GHSA-m95q-7qp3-xv42
- Changelog entry for `express-zod-api` version `10.0.0-beta1`: https://github.com/RobinTail/express-zod-api/blob/master/CHANGELOG.md#v1000-beta1

## References
- https://github.com/RobinTail/express-zod-api/security/advisories/GHSA-mvrp-3cvx-c325
- https://github.com/colinhacks/zod/issues/2609
- https://github.com/colinhacks/zod/pull/2824
- https://github.com/RobinTail/express-zod-api
- https://github.com/advisories/GHSA-m95q-7qp3-xv42
