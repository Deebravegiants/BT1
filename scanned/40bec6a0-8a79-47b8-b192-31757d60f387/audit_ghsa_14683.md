# [C] Apache MINA Deserialization RCE Vulnerability

## Summary
Severity: Critical
Advisory: GHSA-76h9-2vwh-w278
CVE: CVE-2024-52046
CWE: CWE-502, CWE-94
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2024-12-25
Source: https://github.com/advisories/GHSA-76h9-2vwh-w278
Type: github-advisory

## Affected
- Maven: `org.apache.mina:mina-core` — affected >=2.2.0 <2.2.4
- Maven: `org.apache.mina:mina-core` — affected >=2.1.0 <2.1.10
- Maven: `org.apache.mina:mina-core` — affected >=2.0.0-M1 <2.0.27

## Details
The `ObjectSerializationDecoder` in Apache MINA uses Java’s native deserialization protocol to process incoming serialized data but lacks the necessary security checks and defenses. This vulnerability allows attackers to exploit the deserialization process by sending specially crafted malicious serialized data, potentially leading to remote code execution (RCE) attacks.
	
This issue affects MINA core versions 2.0.X, 2.1.X and 2.2.X, and will be fixed by the releases 2.0.27, 2.1.10 and 2.2.4.

It's also important to note that an application using MINA core library will only be affected if the IoBuffer#getObject() method is called, and this specific method is potentially called when adding a ProtocolCodecFilter instance using the `ObjectSerializationCodecFactory` class in the filter chain. If your application is specifically using those classes, you have to upgrade to the latest version of MINA core library.

Upgrading will  not be enough: you also need to explicitly allow the classes the decoder will accept in the ObjectSerializationDecoder instance, using one of the three new methods:

1. 
     * Accept class names where the supplied ClassNameMatcher matches for deserialization, unless they are otherwise rejected.
     * `@param classNameMatcher` the matcher to use
     * / `public void accept(ClassNameMatcher classNameMatcher)`

2. 
     * Accept class names that match the supplied pattern for deserialization, unless they are otherwise rejected.
     * `@param` pattern standard Java regexp
     * / `public void accept(Pattern pattern)`

3.
     * Accept the wildcard specified classes for deserialization, unless they are otherwise rejected.
     * `@param` patterns Wildcard file name patterns as defined by `{@link org.apache.commons.io.FilenameUtils#wildcardMatch(String, String) FilenameUtils.wildcardMatch}`
     * / `public void accept(String... patterns)`

By default, the decoder will reject *all* classes that will be present in the incoming data.

Note: The FtpServer, SSHd and Vysper sub-project are not affected by this issue.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-52046
- https://github.com/apache/mina
- https://lists.apache.org/thread/4wxktgjpggdbto15d515wdctohb0qmv8
- https://security.netapp.com/advisory/ntap-20250103-0001
- http://www.openwall.com/lists/oss-security/2024/12/25/1
