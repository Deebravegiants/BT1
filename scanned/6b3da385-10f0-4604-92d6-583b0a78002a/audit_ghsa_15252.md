# [M] Missing hostname validation in Kroxylicious

## Summary
Severity: Medium
Advisory: GHSA-h83p-72jv-g7vp
CVE: CVE-2024-8285
CWE: CWE-295, CWE-297
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:H/PR:H/UI:R/S:C/C:H/I:H/A:N (CVSS_V3)
Published: 2024-08-31
Source: https://github.com/advisories/GHSA-h83p-72jv-g7vp
Type: github-advisory

## Affected
- Maven: `io.kroxylicious:kroxylicious-runtime` — affected >=0 <0.8.0

## Details
A flaw was found in Kroxylicious. When establishing the connection with the upstream Kafka server using a TLS secured connection, Kroxylicious fails to properly verify the server's hostname, resulting in an insecure connection. For a successful attack to be performed, the attacker needs to perform a Man-in-the-Middle attack or compromise any external systems, such as DNS or network routing configuration. This issue is considered a high complexity attack, with additional high privileges required, as the attack would need access to the Kroxylicious configuration or a peer system. The result of a successful attack impacts both data integrity and confidentiality.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-8285
- https://github.com/kroxylicious/kroxylicious/commit/8be1efcb0a2160fa3ad4cb0e5a27e60160774dce
- https://access.redhat.com/errata/RHSA-2024:9571
- https://access.redhat.com/security/cve/CVE-2024-8285
- https://bugzilla.redhat.com/show_bug.cgi?id=2308606
- https://github.com/kroxylicious/kroxylicious
