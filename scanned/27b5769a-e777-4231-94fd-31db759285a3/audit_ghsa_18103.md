# [C] Apache IoTDB: Deserialization of untrusted Data

## Summary
Severity: Critical
Advisory: GHSA-776q-jw43-fhjx
CVE: CVE-2025-48459
CWE: CWE-502
Ecosystem: Maven, PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2025-09-24
Source: https://github.com/advisories/GHSA-776q-jw43-fhjx
Type: github-advisory

## Affected
- Maven: `org.apache.iotdb:iotdb-confignode` — affected >=1.0.0 <2.0.5
- PyPI: `apache-iotdb` — affected >=1.0.0 <2.0.5

## Details
### Summary

Apache IoTDB deserializes data from external inputs without sufficient validation, allowing attacker-controlled serialized objects to be processed. In environments where a compatible gadget chain is reachable, this can be abused to execute arbitrary code or alter server state; at minimum it enables high-impact integrity and confidentiality compromise on the IoTDB process.

### Affected

Apache IoTDB **from 1.0.0 before 2.0.5**.

### Remediation

Upgrade to **2.0.5**, which addresses the flaw. If immediate upgrade is not possible, restrict exposure of IoTDB endpoints to trusted networks and disable or sanitize any feature paths that accept serialized payloads. These mitigations are defense-in-depth only; upgrading to 2.0.5 is the definitive fix.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-48459
- https://github.com/apache/iotdb/commit/5ad4a940ed84abca27c7e8be86cb371a49900491
- https://github.com/advisories/GHSA-776q-jw43-fhjx
- https://github.com/apache/iotdb
- https://github.com/pypa/advisory-database/tree/main/vulns/apache-iotdb/PYSEC-2025-88.yaml
- https://lists.apache.org/thread/mr84n19nv8d0bmcrfsj3mm5ff5qn4q2f
- http://www.openwall.com/lists/oss-security/2025/09/24/8
