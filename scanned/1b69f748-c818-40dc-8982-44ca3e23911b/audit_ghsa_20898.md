# [H] Parse Server vulnerable to brute force guessing of user sensitive data via search patterns

## Summary
Severity: High
Advisory: GHSA-2m6g-crv8-p3c6
CVE: CVE-2022-36079
CWE: CWE-200
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:N/A:N (CVSS_V3)
Published: 2022-09-16
Source: https://github.com/advisories/GHSA-2m6g-crv8-p3c6
Type: github-advisory

## Affected
- npm: `parse-server` — affected >=0 <4.10.14
- npm: `parse-server` — affected >=5.0.0 <5.2.5

## Details
### Impact

Internal fields (keys used internally by Parse Server, prefixed by `_`) and protected fields (user defined) can be used as query constraints. Internal and protected fields are removed by Parse Server from query results and are only returned to the client using a valid master key. However, using query constraints, these fields can be guessed by enumerating until Parse Server returns a response object.

### Patches

The patch requires the master key to use internal and protected fields as query constraints.

### Workarounds

Implement a Parse Cloud Trigger `beforeFind` and manually remove the query constraints, such as:

```js
Parse.Cloud.beforeFind('TestObject', ({ query }) => {
  for (const key in query._where || []) {
    // Repeat logic for protected fields
    if (key.charAt(0) === '_') {
      delete query._where[key];
    }
  }
});
```

### References

- https://github.com/parse-community/parse-server/security/advisories/GHSA-2m6g-crv8-p3c6

## References
- https://github.com/parse-community/parse-server/security/advisories/GHSA-2m6g-crv8-p3c6
- https://nvd.nist.gov/vuln/detail/CVE-2022-36079
- https://github.com/parse-community/parse-server/issues/8143
- https://github.com/parse-community/parse-server/issues/8144
- https://github.com/parse-community/parse-server/commit/634c44acd18f6ee6ec60fac89a2b602d92799bec
- https://github.com/parse-community/parse-server/commit/e39d51bd329cd978589983bd659db46e1d45aad4
- https://github.com/parse-community/parse-server
- https://github.com/parse-community/parse-server/releases/tag/4.10.14
- https://github.com/parse-community/parse-server/releases/tag/5.2.5
