# [C] Critical vulnerability in log4j may affect generated PEAR projects

## Summary
Severity: Critical
Advisory: GHSA-j7c3-96rf-jrrp
Ecosystem: Maven
Published: 2021-12-16
Source: https://github.com/advisories/GHSA-j7c3-96rf-jrrp
Type: github-advisory

## Affected
- Maven: `de.averbis.textanalysis:pear-archetype` — affected >=2.0.0 <2.0.1

## Details
### Impact
UIMA PEAR projects that have been generated with the `de.averbis.textanalysis:pear-archetype ` version `2.0.0` have a maven dependency with scope `test` to` log4j 2.8.2` and might be affected by CVE-2021-44228.

### Patches
- The issue has been resolved in `de.averbis.textanalysis:pear-archetype ` version `2.0.1`. Please make sure to use `de.averbis.textanalysis:pear-archetype ` version >= `2.0.1` for generating new PEAR projects.

- Existing maven PEAR projects can be patched by manually upgrading to `log4j` >= `2.16.0` in `pom.xml`.


### References
https://www.lunasec.io/docs/blog/log4j-zero-day/

### For more information
If you have any questions or comments about this advisory:
* Open an issue in https://github.com/averbis/pear-archetype/issues

## References
- https://github.com/averbis/pear-archetype/security/advisories/GHSA-j7c3-96rf-jrrp
- https://github.com/averbis/pear-archetype/commit/6815f5981c836ab8c345a6ff54f29e9f4b67f7eb
- https://github.com/averbis/pear-archetype
