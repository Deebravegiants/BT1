# [M] Insufficiently Protected Credentials via Insecure Temporary File in org.apache.nifi:nifi-single-user-utils

## Summary
Severity: Medium
Advisory: GHSA-rvp4-r3g6-8hxq
CVE: CVE-2022-26850
CWE: CWE-522
Ecosystem: Maven
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:C/C:H/I:N/A:N (CVSS_V3)
Published: 2022-06-20
Source: https://github.com/advisories/GHSA-rvp4-r3g6-8hxq
Type: github-advisory

## Affected
- Maven: `org.apache.nifi:nifi-single-user-utils` — affected >=0 <1.16

## Details
### Impact

`org.apache.nifi.authentication.single.user.writer.StandardLoginCredentialsWriter` contains a local information disclosure vulnerability due to writing credentials (username and password) to a file that is readable by all other users on unix-like systems. On unix-like systems, the system's temporary directory is shared between all users on that system. As such, files written to that directory without setting the correct file permissions can allow other users on that system to view the contents of the files written to those temporary files.

### Source

An insecure temporary file is created here:
 - https://github.com/apache/nifi/blob/6a1c7c72d5b91b9ce5d5cb5b86e3155d21e2c19b/nifi-commons/nifi-single-user-utils/src/main/java/org/apache/nifi/authentication/single/user/writer/StandardLoginCredentialsWriter.java#L75

The username and password credentials are written to this file here:
 - https://github.com/apache/nifi/blob/6a1c7c72d5b91b9ce5d5cb5b86e3155d21e2c19b/nifi-commons/nifi-single-user-utils/src/main/java/org/apache/nifi/authentication/single/user/writer/StandardLoginCredentialsWriter.java#L85-L95

### Patches

The vulnerability has been patched in version `1.16`.

### Prerequisites

This vulnerability impacts Unix-like systems, and very old versions of Mac OSX and Windows as they all share the system temporary directory between all users.

### Workarounds

Setting the `java.io.tmpdir` system environment variable to a directory that is exclusively owned by the executing user will fix this vulnerability for all operating systems.

### References

 - https://issues.apache.org/jira/browse/NIFI-9785
 - https://github.com/apache/nifi/commit/859d5fe
 - https://github.com/apache/nifi/pull/5856
 - https://nifi.apache.org/security.html#CVE-2022-26850
 - https://twitter.com/JLLeitschuh/status/1511736635645435904?s=20&t=I3w3zF6Y2DUvWYsEFqERjg

## References
- https://github.com/JLLeitschuh/security-research/security/advisories/GHSA-rvp4-r3g6-8hxq
- https://nvd.nist.gov/vuln/detail/CVE-2022-26850
- https://github.com/apache/nifi/commit/859d5fe
- https://github.com/apache/nifi/commit/859d5fe8cfe05ad24600b021f0ebf15753a8105c
- https://nifi.apache.org/security.html#CVE-2022-26850
- http://www.openwall.com/lists/oss-security/2022/04/06/2
