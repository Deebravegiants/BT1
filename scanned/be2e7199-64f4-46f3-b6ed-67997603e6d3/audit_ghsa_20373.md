# [H] pg-native and libpq vulnerable to uncontrolled resource consumption

## Summary
Severity: High
Advisory: GHSA-j32j-2hxv-rqf7
CVE: CVE-2022-25852
CWE: CWE-400, CWE-704
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-06-18
Source: https://github.com/advisories/GHSA-j32j-2hxv-rqf7
Type: github-advisory

## Affected
- npm: `libpq` — affected >=0 <1.8.10
- npm: `pg-native` — affected >=0 <3.0.1

## Details
pg-native before 3.0.1 and libpq before 1.8.10 are vulnerable to Denial of Service (DoS) when the addons attempt to cast the second argument to an array and fail. This happens for every non-array argument passed. **Note:** pg-native is a mere binding to npm's libpq library, which in turn has the addons and bindings to the actual C libpq library. This means that problems found in pg-native may transitively impact npm's libpq.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-25852
- https://github.com/brianc/node-libpq/issues/84
- https://github.com/brianc/node-libpq/pull/86
- https://snyk.io/vuln/SNYK-JS-LIBPQ-2392366
- https://snyk.io/vuln/SNYK-JS-PGNATIVE-2392365
