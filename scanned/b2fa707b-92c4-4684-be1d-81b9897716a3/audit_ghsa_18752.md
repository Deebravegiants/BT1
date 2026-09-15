# [C] Apache Pyfory python is vulnerable to deserialization of untrusted data

## Summary
Severity: Critical
Advisory: GHSA-538v-3wq9-4h3r
CVE: CVE-2025-61622
CWE: CWE-502
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2025-10-01
Source: https://github.com/advisories/GHSA-538v-3wq9-4h3r
Type: github-advisory

## Affected
- PyPI: `pyfory` — affected >=0.12.0 <0.12.3
- PyPI: `pyfury` — affected >=0.1.0

## Details
Deserialization of untrusted data in python in pyfory versions 0.12.0 through 0.12.2, or the legacy pyfury versions from 0.1.0 through 0.10.3: allows arbitrary code execution. An application is vulnerable if it reads pyfory serialized data from untrusted sources. An attacker can craft a data stream that selects pickle-fallback serializer during deserialization, leading to the execution of `pickle.loads`, which is vulnerable to remote code execution.

Users are recommended to upgrade to pyfory version 0.12.3 or later, which has removed pickle fallback serializer and thus fixes this issue.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-61622
- https://github.com/apache/fory/pull/2629
- https://github.com/apache/fory/commit/379b948ecae5c3b849e5bdb3997978c9a163e40b
- https://github.com/apache/fory
- https://github.com/apache/fory/releases/tag/v0.12.3
- https://lists.apache.org/thread/vfn9hp9qt06db5yo1gmj3l114o3o2csd
- http://www.openwall.com/lists/oss-security/2025/09/29/3
