# [M] Venice vulnerable to Partial Path Traversal issue within the functions `load-file` and `load-resource`

## Summary
Severity: Medium
Advisory: GHSA-4mmh-5vw7-rgvj
CVE: CVE-2022-36007
CWE: CWE-22
Ecosystem: Maven
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:L/I:H/A:N (CVSS_V3)
Published: 2022-08-18
Source: https://github.com/advisories/GHSA-4mmh-5vw7-rgvj
Type: github-advisory

## Affected
- Maven: `com.github.jlangch:venice` — affected >=0 <1.10.17

## Details
### Impact
A partial path traversal issue exists within the functions `load-file` and `load-resource`. These functions can be limited to load files from a list of load paths.

Assuming Venice has been configured with the load paths: `[ "/Users/foo/resources" ]` 

When passing **relative** paths to these two vulnerable functions everything is fine:
`(load-resource "test.png")`   => loads the file "/Users/foo/resources/test.png"
`(load-resource "../resources-alt/test.png")`   => rejected, outside the load path

When passing **absolute** paths to these two vulnerable functions Venice may return files outside the configured load paths:
`(load-resource "/Users/foo/resources/test.png")`   => loads the file "/Users/foo/resources/test.png"
`(load-resource "/Users/foo/resources-alt/test.png")`   => loads the file "/Users/foo/resources-alt/test.png" !!!
The latter call suffers from the _Partial Path Traversal_ vulnerability.

This issue’s scope is limited to absolute paths whose name prefix matches a load path. E.g. for a load-path `"/Users/foo/resources"`, the actor can cause loading a resource also from `"/Users/foo/resources-alt"`, but not from `"/Users/foo/images"`.

Versions of Venice before and including v1.10.16 are affected by this issue.

### Patches
Upgrade to Venice >= 1.10.17, if you are on a version < 1.10.17

### Workarounds
If you cannot upgrade the library, you can control the functions that can be used in Venice with a sandbox. If it is appropriate, the functions `load-file` and `load-resource` can be blacklisted in the sandbox.

### References
  * [PR](https://github.com/jlangch/venice/pull/4/commits/c942c73136333bc493050910f171a48e6f575b23)
 
### For more information
If you have any questions or comments about this advisory:
* Open an issue in [GitHub Venice](https://github.com/jlangch/venice)
* Email us at [juerg.ch](mailto:juerg.ch@ggaweb.ch)

### Credits

I want to publicly recognize the contribution of [Jonathan Leitschuh](https://github.com/JLLeitschuh) for reporting this issue.

## References
- https://github.com/jlangch/venice/security/advisories/GHSA-4mmh-5vw7-rgvj
- https://nvd.nist.gov/vuln/detail/CVE-2022-36007
- https://github.com/jlangch/venice/commit/215ae91bb964013b0a2d70718a692832d561ae0a
- https://github.com/jlangch/venice/commit/c942c73136333bc493050910f171a48e6f575b23
- https://github.com/jlangch/venice
- https://github.com/jlangch/venice/releases/tag/v1.10.17
