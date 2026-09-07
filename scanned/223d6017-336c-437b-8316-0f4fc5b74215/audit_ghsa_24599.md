# [H] fabric8-maven-plugin: insecure way to construct Yaml Object leading to remote code execution

## Summary
Severity: High
Advisory: GHSA-w7gj-h6f2-x4c6
CVE: CVE-2020-10721
CWE: CWE-502
Ecosystem: Maven
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-w7gj-h6f2-x4c6
Type: github-advisory

## Affected
- Maven: `io.fabric8:fabric8-maven-plugin` — affected >=4.0.0-M1

## Details
A flaw was found in the fabric8-maven-plugin 4.0.0 and later. When using a wildfly-swarm or thorntail custom configuration, a malicious YAML configuration file on the local machine executing the maven plug-in could allow for deserialization of untrusted data resulting in arbitrary code execution. The highest threat from this vulnerability is to data confidentiality and integrity as well as system availability.

The fabric8-maven-plugin has been superseded by the Eclipse project JKube and the recommendation is migrating users of the fabric8-maven-plugin to Eclipse Jkube >= 1.0.0

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-10721
- https://bugzilla.redhat.com/show_bug.cgi?id=1827201
- https://github.com/fabric8io/fabric8-maven-plugin
