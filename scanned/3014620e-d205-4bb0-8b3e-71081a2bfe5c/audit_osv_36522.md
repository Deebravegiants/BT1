# [C] Apache IoTDB: Path Traversal in DataNode Internal RPC Trigger JAR Upload Allows Arbitrary File Write

## Summary
Severity: Critical
Advisory: CVE-2026-24014
Aliases: PYSEC-2026-2081
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-07-06
Source: https://osv.dev/vulnerability/CVE-2026-24014
Type: osv

## Details
Apache IoTDB DataNode’s internal RPC interface for creating Trigger instances uses the uploaded Trigger JAR name to build a file path without sufficient validation. If the internal DataNode RPC port is exposed to an untrusted network, an attacker may use path traversal sequences in the JAR name to write files outside the intended Trigger installation directory. This could allow arbitrary file write with the permissions of the IoTDB process.

This issue affects Apache IoTDB: from 1.3.3 before 2.0.8.

Users are recommended to upgrade to version 2.0.8, which fixes the issue.

## References
- http://www.openwall.com/lists/oss-security/2026/07/06/12
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/24xxx/CVE-2026-24014.json
- https://lists.apache.org/thread/38298f803gb5j9nlhf0l9zkf34o90h3m
- https://nvd.nist.gov/vuln/detail/CVE-2026-24014
