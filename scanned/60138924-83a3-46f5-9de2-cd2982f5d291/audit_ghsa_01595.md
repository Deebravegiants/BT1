# [H] Prototype pollution in object-path

## Summary
Severity: High
Advisory: GHSA-cwx2-736x-mf6w
CVE: CVE-2020-15256
CWE: CWE-20, CWE-471
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:L/I:H/A:H (CVSS_V3)
Published: 2020-10-19
Source: https://github.com/advisories/GHSA-cwx2-736x-mf6w
Type: github-advisory

## Affected
- npm: `object-path` — affected >=0 <0.11.5

## Details
### Impact
A prototype pollution vulnerability has been found in `object-path` <= 0.11.4 affecting the `set()` method. The vulnerability is limited to the `includeInheritedProps` mode (if version >= 0.11.0 is used), which has to be explicitly enabled by creating a new instance of `object-path` and setting the option `includeInheritedProps: true`, or by using the default `withInheritedProps` instance. The default operating mode is not affected by the vulnerability if version >= 0.11.0 is used. Any usage of `set()` in versions < 0.11.0 is vulnerable.
 
### Patches
Upgrade to version >= 0.11.5

### Workarounds
Don't use the `includeInheritedProps: true` options or the `withInheritedProps` instance if using a version >= 0.11.0.

### References
[Read more about the prototype pollution vulnerability](https://codeburst.io/what-is-prototype-pollution-49482fc4b638)

### For more information
If you have any questions or comments about this advisory:
* Open an issue in [object-path](https://github.com/mariocasciaro/object-path)

## References
- https://github.com/mariocasciaro/object-path/security/advisories/GHSA-cwx2-736x-mf6w
- https://nvd.nist.gov/vuln/detail/CVE-2020-15256
- https://github.com/mariocasciaro/object-path/commit/2be3354c6c46215c7635eb1b76d80f1319403c68
- https://github.com/mariocasciaro/object-path
