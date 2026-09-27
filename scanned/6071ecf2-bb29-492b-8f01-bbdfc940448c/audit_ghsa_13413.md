# [M] OpenRefine vulnerable to zip slip in project import

## Summary
Severity: Medium
Advisory: GHSA-m88m-crr9-jvqq
CVE: CVE-2023-37476
CWE: CWE-22
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2023-07-18
Source: https://github.com/advisories/GHSA-m88m-crr9-jvqq
Type: github-advisory

## Affected
- Maven: `org.openrefine:main` — affected >=0 <3.7.4

## Details
### Impact

A carefully crafted malicious OpenRefine project tar file can be used to trigger arbitrary code execution if a user can be convinced to import it.

### Patches

The vulnerability exists in all versions of OpenRefine up to and including 3.7.3. Users should update to OpenRefine 3.7.4 as soon as possible.

### Workarounds

Only import OpenRefine projects from trusted sources.

### References

A similar [issue](https://github.com/OpenRefine/OpenRefine/issues/1840) existed in the Create Project feature ([CVE-2018-19859](https://nvd.nist.gov/vuln/detail/CVE-2018-19859)), which was fixed by PR [#1901](https://github.com/OpenRefine/OpenRefine/pull/1901).

## References
- https://github.com/OpenRefine/OpenRefine/security/advisories/GHSA-m88m-crr9-jvqq
- https://nvd.nist.gov/vuln/detail/CVE-2023-37476
- https://github.com/OpenRefine/OpenRefine/commit/e9c1e65d58b47aec8cd676bd5c07d97b002f205e
- https://github.com/OpenRefine/OpenRefine
- https://github.com/OpenRefine/OpenRefine/releases/tag/3.7.4
- https://www.sonarsource.com/blog/openrefine-zip-slip
