# [M] When setting EntityOptions.apiPrefilter to a function, the filter is not applied to API requests for a resource by Id

## Summary
Severity: Medium
Advisory: GHSA-7hh3-3x64-v2g9
CVE: CVE-2023-35167
CWE: CWE-284
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2023-06-20
Source: https://github.com/advisories/GHSA-7hh3-3x64-v2g9
Type: github-advisory

## Affected
- npm: `remult` — affected >=0 <0.20.6

## Details
### Impact
If you used the [apiPrefilter](https://remult.dev/docs/ref_entity.html#apiprefilter) option of the `@Entity` decorator, by setting it to a function that returns a filter that prevents unauthorized access to data, an attacker who knows the `id` of an entity instance she is not authorized to access, can gain read, update and delete access to it.

### Patches
The issue is fixed in version 0.20.6

### Workarounds
Set the `apiPrefilter` option to a filter object instead of a function.

### References
If you're using a minor version < 0.20 and require a patch, please create an issue.

## References
- https://github.com/remult/remult/security/advisories/GHSA-7hh3-3x64-v2g9
- https://nvd.nist.gov/vuln/detail/CVE-2023-35167
- https://github.com/remult/remult/commit/6892ae97134126d8710ef7302bb2fc37730994c5
- https://github.com/remult/remult
- https://github.com/remult/remult/releases/tag/v0.20.6
