# [C] Apache Fory PyFory Deserialization of Untrusted Data 

## Summary
Severity: Critical
Advisory: GHSA-m5gw-83w2-7749
CVE: CVE-2026-48207
CWE: CWE-502
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-05-21
Source: https://github.com/advisories/GHSA-m5gw-83w2-7749
Type: github-advisory

## Affected
- PyPI: `pyfory` — affected >=0.13.0 <1.0.0

## Details
Fory PyFory's ReduceSerializer could bypass documented DeserializationPolicy validation hooks during reduce-state restoration and global-name resolution. An application is vulnerable if it deserializes attacker-controlled data using PyFory Python-native mode with strict mode disabled and relies on DeserializationPolicy to restrict unsafe classes, functions, or module attributes.

This issue affects Apache Fory: from before 1.0.0.

Mitigation: Users of Apache Fory are recommended to upgrade to version 1.0.0 or later, which enforces DeserializationPolicy validation for the affected ReduceSerializer paths and thus fixes this issue.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-48207
- https://fory.apache.org/security/#cve-2026-48207-pyfory-reduceserializer-deserializationpolicy-bypass
- https://github.com/apache/fory
- http://www.openwall.com/lists/oss-security/2026/05/21/10
