# [H] HL7 FHIR Partial Path Zip Slip due to bypass of CVE-2023-24057

## Summary
Severity: High
Advisory: GHSA-9654-pr4f-gh6m
CVE: CVE-2023-28465
CWE: CWE-22
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2023-03-10
Source: https://github.com/advisories/GHSA-9654-pr4f-gh6m
Type: github-advisory

## Affected
- Maven: `ca.uhn.hapi.fhir:org.hl7.fhir.core` — affected >=0 <5.6.106
- Maven: `ca.uhn.hapi.fhir:org.hl7.fhir.convertors` — affected >=0 <5.6.106
- Maven: `ca.uhn.hapi.fhir:org.hl7.fhir.r4b` — affected >=0 <5.6.106
- Maven: `ca.uhn.hapi.fhir:org.hl7.fhir.r5` — affected >=0 <5.6.106
- Maven: `ca.uhn.hapi.fhir:org.hl7.fhir.utilities` — affected >=0 <5.6.106
- Maven: `ca.uhn.hapi.fhir:org.hl7.fhir.validation` — affected >=0 <5.6.106

## Details
### Impact

Zip Slip protections implemented in CVE-2023-24057 (GHSA-jqh6-9574-5x22) can be bypassed due a partial path traversal vulnerability.

This issue allows a malicious actor to potentially break out of the `TerminologyCacheManager` cache directory. The impact is limited to sibling directories.

To demonstrate the vulnerability, consider `userControlled.getCanonicalPath().startsWith("/usr/out")` will allow an attacker to access a directory with a name like `/usr/outnot`. 

### Why?

To demonstrate this vulnerability, consider `"/usr/outnot".startsWith("/usr/out")`.
The check is bypassed although `/outnot` is not under the `/out` directory.
It's important to understand that the terminating slash may be removed when using various `String` representations of the `File` object.
For example, on Linux, `println(new File("/var"))` will print `/var`, but `println(new File("/var", "/")` will print `/var/`;
however, `println(new File("/var", "/").getCanonicalPath())` will print `/var`.

### The Fix

Comparing paths with the `java.nio.files.Path#startsWith` will adequately protect againts this vulnerability.

For example: `file.getCanonicalFile().toPath().startsWith(BASE_DIRECTORY)` or `file.getCanonicalFile().toPath().startsWith(BASE_DIRECTORY_FILE.getCanonicalFile().toPath())`

### Other Examples

 - [CVE-2022-31159](https://github.com/aws/aws-sdk-java/security/advisories/GHSA-c28r-hw5m-5gv3) - aws/aws-sdk-java
 - [CVE-2022-23457](https://securitylab.github.com/advisories/GHSL-2022-008_The_OWASP_Enterprise_Security_API/) - ESAPI/esapi-java-legacy

### Vulnerability

https://github.com/hapifhir/org.hl7.fhir.core/blob/b0daf666725fa14476d147522155af1e81922aac/org.hl7.fhir.r4b/src/main/java/org/hl7/fhir/r4b/terminologies/TerminologyCacheManager.java#L99-L105

While `getAbsolutePath` will return a normalized path, because the string `path` is not slash terminated, the guard can be bypassed to write the contents of the Zip file to a sibling directory of the cache directory.

### Patches
All org.hl7.fhir.core libraries should be updated to 5.6.106.
 - https://github.com/hapifhir/org.hl7.fhir.core/pull/1162

### Workarounds
Unknown

### References
* https://snyk.io/research/zip-slip-vulnerability

## References
- https://github.com/hapifhir/org.hl7.fhir.core/security/advisories/GHSA-9654-pr4f-gh6m
- https://nvd.nist.gov/vuln/detail/CVE-2023-28465
- https://github.com/hapifhir/org.hl7.fhir.core/pull/1162
- https://github.com/advisories/GHSA-9654-pr4f-gh6m
- https://github.com/hapifhir/org.hl7.fhir.core
- https://github.com/hapifhir/org.hl7.fhir.core/blob/b0daf666725fa14476d147522155af1e81922aac/org.hl7.fhir.r4b/src/main/java/org/hl7/fhir/r4b/terminologies/TerminologyCacheManager.java#L99-L105
- https://github.com/hapifhir/org.hl7.fhir.core/releases/tag/5.6.106
- https://www.smilecdr.com/our-blog
- https://www.smilecdr.com/our-blog/statement-on-cve-2023-24057-smile-digital-health
