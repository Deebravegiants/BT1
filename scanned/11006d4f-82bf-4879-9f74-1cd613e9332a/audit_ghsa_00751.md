# [M] XML external entity (XXE) processing ('external-parameter-entities' feature was not fully disabled))

## Summary
Severity: Medium
Advisory: GHSA-763g-fqq7-48wg
CVE: CVE-2019-10782
CWE: CWE-611
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2020-01-31
Source: https://github.com/advisories/GHSA-763g-fqq7-48wg
Type: github-advisory

## Affected
- Maven: `com.puppycrawl.tools:checkstyle` — affected >=0 <8.29

## Details
Due to an incomplete fix for [CVE-2019-9658](https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2019-9658), checkstyle was still vulnerable to XML External Entity (XXE) Processing.

### Impact

#### User: Build Maintainers

This vulnerability probably doesn't impact Maven/Gradle users as, in most cases, these builds are processing files that are trusted, or pre-vetted by a pull request reviewer before being run on internal CI infrastructure.

#### User: Static Analysis as a Service

If you operate a site/service that parses "untrusted" Checkstyle XML configuration files, you are vulnerable to this and should patch.

Note from the discoverer of the original CVE-2019-9658:

> While looking at a few companies that run Checkstyle/PMD/ect... as a service I notice that it's a common pattern to run the static code analysis tool inside of a Docker container with the following flags:
> ```
> --net=none \
> --privileged=false \
> --cap-drop=ALL
> ```
> Running the analysis in Docker has the advantage that there should be no sensitive local file information that XXE can exfiltrate from the container. Additionally, these flags prevent vulnerabilities in static analysis tools like Checkstyle from being used to exfiltrate data via XXE or to perform SSRF.
> \- [Jonathan Leitschuh](https://twitter.com/jlleitschuh)

### Patches
_Has the problem been patched? What versions should users upgrade to?_

Patched, will be released with version 8.29 at 26 Jan 2020.

### Workarounds
_Is there a way for users to fix or remediate the vulnerability without upgrading?_

No workaround are available

### References

 - [CWE-611: Improper Restriction of XML External Entity Reference](https://cwe.mitre.org/data/definitions/611.html)
 - GitHub Issue https://github.com/checkstyle/checkstyle/issues/7468

### For more information

If you have any questions or comments about this advisory:
* Open an issue in https://github.com/checkstyle/checkstyle/issues

## References
- https://github.com/checkstyle/checkstyle/security/advisories/GHSA-763g-fqq7-48wg
- https://nvd.nist.gov/vuln/detail/CVE-2019-10782
- https://github.com/checkstyle/checkstyle/issues/7468
- https://github.com/checkstyle/checkstyle/commit/c46a16d177e6797895b195c288ae9a9a096254b8
- https://lists.apache.org/thread.html/r8aaf4ee16bbaf6204731d4770d96ebb34b258cd79b491f9cdd7f2540@%3Ccommits.nifi.apache.org%3E
- https://lists.debian.org/debian-lts-announce/2020/02/msg00008.html
- https://snyk.io/vuln/SNYK-JAVA-COMPUPPYCRAWLTOOLS-543266
