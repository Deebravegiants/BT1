# [H] TestNG is vulnerable to Path Traversal

## Summary
Severity: High
Advisory: GHSA-rc2q-x9mf-w3vf
CVE: CVE-2022-4065
CWE: CWE-22
Ecosystem: Maven
CVSS: CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-11-19
Source: https://github.com/advisories/GHSA-rc2q-x9mf-w3vf
Type: github-advisory

## Affected
- Maven: `org.testng:testng` — affected >=6.13 <7.5.1
- Maven: `org.testng:testng` — affected >=7.6.0 <7.7.0

## Details
### Impact

Affected by this vulnerability is the function `testngXmlExistsInJar` of the file `testng-core/src/main/java/org/testng/JarFileUtils.java` of the component `XML File Parser`.

The manipulation leads to path traversal only for `.xml`, `.yaml` and `.yml` files by default. The attack implies running an unsafe test JAR. However since that JAR can also contain executable code itself, the path traversal is unlikely to be the main attack.

### Patches

A patch is available in [version 7.7.0](https://github.com/cbeust/testng/releases/tag/7.7.0) at commit 9150736cd2c123a6a3b60e6193630859f9f0422b. It is recommended to apply a patch to fix this issue. The patch was pushed into the master branch but no releases have yet been made with the patch included.

A backport of the fix is available in [version 7.5.1]((https://github.com/cbeust/testng/releases/tag/7.5.1) for Java 8 projects.

### Workaround

* Specify which tests to run when invoking TestNG by configuring them on the CLI or in the build tool controlling the run.
* Do not run tests with untrusted JARs on the classpath, this includes pull requests on open source projects.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-4065
- https://github.com/cbeust/testng/pull/1596
- https://github.com/cbeust/testng/pull/2806
- https://github.com/testng-team/testng/pull/2899
- https://github.com/cbeust/testng/commit/9150736cd2c123a6a3b60e6193630859f9f0422b
- https://github.com/cbeust/testng
- https://github.com/cbeust/testng/releases/tag/7.7.0
- https://github.com/cbeust/testng/releases/tag/7.7.1
- https://github.com/testng-team/testng/releases/tag/7.5.1
- https://vuldb.com/?ctiid.214027
- https://vuldb.com/?id.214027
