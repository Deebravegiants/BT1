# [M] OpenNMS Horizon vulnerable to XSS

## Summary
Severity: Medium
Advisory: GHSA-9hhc-cc6c-99hh
CVE: CVE-2021-25934
CWE: CWE-79
Ecosystem: Maven
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-9hhc-cc6c-99hh
Type: github-advisory

## Affected
- Maven: `org.opennms:opennms` — affected >=18.0.0-1

## Details
In OpenNMS Horizon, versions opennms-18.0.0-1 through opennms-27.1.0-1; OpenNMS Meridian, versions meridian-foundation-2015.1.0-1 through meridian-foundation-2019.1.18-1; meridian-foundation-2020.1.0-1 through meridian-foundation-2020.1.7-1 are vulnerable to Stored Cross-Site Scripting, since the function `createRequisitionedNode()` does not perform any validation checks on the input sent to the `node-label` parameter. Due to this flaw an attacker could inject an arbitrary script which will be stored in the database.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-25934
- https://github.com/OpenNMS/opennms/commit/101e3aa06ec9a1f8f266335fc6f5685c062c6117
- https://github.com/OpenNMS/opennms/commit/eb08b5ed4c5548f3e941a1f0d0363ae4439fa98c
- https://www.whitesourcesoftware.com/vulnerability-database/CVE-2021-25934
