# [H] Insertion of Sensitive Information into Log File in Apache NiFi Stateless

## Summary
Severity: High
Advisory: GHSA-g644-pr5v-vppf
CVE: CVE-2020-9486
CWE: CWE-532
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-01-06
Source: https://github.com/advisories/GHSA-g644-pr5v-vppf
Type: github-advisory

## Affected
- Maven: `org.apache.nifi:nifi-stateless` — affected >=1.10.0 <1.12.0-RC1

## Details
In Apache NiFi 1.10.0 to 1.11.4, the NiFi stateless execution engine produced log output which included sensitive property values. When a flow was triggered, the flow definition configuration JSON was printed, potentially containing sensitive values in plaintext.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-9486
- https://github.com/apache/nifi/commit/148537d64a017b73160b0d49943183c18f883ab0
- https://github.com/apache/nifi
- https://nifi.apache.org/security#CVE-2020-9486
