# [C] Code injection in Apache Commons Configuration

## Summary
Severity: Critical
Advisory: GHSA-xj57-8qj4-c4m6
CVE: CVE-2022-33980
CWE: CWE-74
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-07-07
Source: https://github.com/advisories/GHSA-xj57-8qj4-c4m6
Type: github-advisory

## Affected
- Maven: `org.apache.commons:commons-configuration2` — affected >=2.4 <2.8.0

## Details
Apache Commons Configuration performs variable interpolation, allowing properties to be dynamically evaluated and expanded. The standard format for interpolation is "${prefix:name}", where "prefix" is used to locate an instance of org.apache.commons.configuration2.interpol.Lookup that performs the interpolation. Starting with version 2.4 and continuing through 2.7, the set of default Lookup instances included interpolators that could result in arbitrary code execution or contact with remote servers. These lookups are: - "script" - execute expressions using the JVM script execution engine (javax.script) - "dns" - resolve dns records - "url" - load values from urls, including from remote servers Applications using the interpolation defaults in the affected versions may be vulnerable to remote code execution or unintentional contact with remote servers if untrusted configuration values are used. Users are recommended to upgrade to Apache Commons Configuration 2.8.0, which disables the problematic interpolators by default.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-33980
- https://commons.apache.org/proper/commons-configuration/changes-report.html#a2.8.0
- https://github.com/apache/commons-configuration
- https://issues.apache.org/jira/browse/CONFIGURATION-753
- https://issues.apache.org/jira/browse/CONFIGURATION-764
- https://lists.apache.org/thread/tdf5n7j80lfxdhs2764vn0xmpfodm87s
- https://security.netapp.com/advisory/ntap-20221028-0015
- https://www.debian.org/security/2022/dsa-5290
- http://www.openwall.com/lists/oss-security/2022/07/06/5
- http://www.openwall.com/lists/oss-security/2022/11/15/4
