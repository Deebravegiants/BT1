# [M] Infinispan CLI vulnerable to Generation of Error Message Containing Sensitive Information

## Summary
Severity: Medium
Advisory: GHSA-cqm8-rg2p-jfcf
CVE: CVE-2025-5731
CWE: CWE-209
Ecosystem: Maven
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2025-06-27
Source: https://github.com/advisories/GHSA-cqm8-rg2p-jfcf
Type: github-advisory

## Affected
- Maven: `org.infinispan:infinispan-cli-client` — affected >=0

## Details
A flaw was found in Infinispan CLI. A sensitive password, decoded from a Base64-encoded Kubernetes secret, is processed in plaintext and included in a command string that may expose the data in an error message when a command is not found.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-5731
- https://access.redhat.com/errata/RHSA-2025:10130
- https://access.redhat.com/security/cve/CVE-2025-5731
- https://bugzilla.redhat.com/show_bug.cgi?id=2370429
- https://github.com/infinispan/infinispan
