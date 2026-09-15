# [M] Drools Core Deserialization of Untrusted Data vulnerability

## Summary
Severity: Medium
Advisory: GHSA-m5q8-58wh-xxq4
CVE: CVE-2022-1415
CWE: CWE-502
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2023-09-11
Source: https://github.com/advisories/GHSA-m5q8-58wh-xxq4
Type: github-advisory

## Affected
- Maven: `org.drools:drools-core` — affected >=0 <7.69.0.Final

## Details
A flaw was found where some utility classes in Drools core did not use proper safeguards when deserializing data. This flaw allows an authenticated attacker to construct malicious serialized objects (usually called gadgets) and achieve code execution on the server.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-1415
- https://access.redhat.com/errata/RHSA-2022:6813
- https://access.redhat.com/security/cve/CVE-2022-1415
- https://bugzilla.redhat.com/show_bug.cgi?id=2065505
