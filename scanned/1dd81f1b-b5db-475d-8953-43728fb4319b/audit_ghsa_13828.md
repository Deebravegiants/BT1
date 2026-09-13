# [H] Quarkus does not properly sanitize artifacts created from its use of the Gradle plugin, allowing certain build system information to remain

## Summary
Severity: High
Advisory: GHSA-p62q-5483-h57v
CVE: CVE-2023-5720
CWE: CWE-526
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:N/A:N (CVSS_V3)
Published: 2023-11-15
Source: https://github.com/advisories/GHSA-p62q-5483-h57v
Type: github-advisory

## Affected
- Maven: `io.quarkus:quarkus-project` — affected >=3.0.0.CR1

## Details
A flaw was found in Quarkus, where it does not properly sanitize artifacts created using the Gradle plugin, allowing certain build system information to remain. This flaw allows an attacker to access potentially sensitive information from the build system within the application.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-5720
- https://access.redhat.com/security/cve/CVE-2023-5720
- https://bugzilla.redhat.com/show_bug.cgi?id=2245700
- https://github.com/quarkusio/quarkus
