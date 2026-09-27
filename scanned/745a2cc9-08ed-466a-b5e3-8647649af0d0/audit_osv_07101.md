# [M] Apache NiFi: Incorrect Authorization for Configuration Verification Requests

## Summary
Severity: Medium
Advisory: BIT-nifi-2026-44911
Aliases: CVE-2026-44911, GHSA-qvj8-gwpm-4x49
Ecosystem: Bitnami
Published: 2026-06-24
Source: https://osv.dev/vulnerability/BIT-nifi-2026-44911
Type: osv

## Affected
- Bitnami: `nifi` — affected >=1.15.0 <2.10.0

## Details
Authorization handling for component configuration verification requests in Apache NiFi 1.15.0 through 2.9.0 allows clients with read access to submit proposed configuration properties. The proposed properties override current configuration, enabling users with read access to invoke predefined verification methods with alternative settings. Apache NiFi installations that do not implement different levels of authorization for viewing and modifying component configuration are not subject to this vulnerability. Upgrading to Apache NiFi 2.10.0 is the recommended mitigation, requiring write access to submit configuration verification requests.

## References
- http://www.openwall.com/lists/oss-security/2026/06/20/4
- https://lists.apache.org/thread/wrj3t4k2bwd2cztyp078f5kj3722qfzy
- https://nvd.nist.gov/vuln/detail/CVE-2026-44911
