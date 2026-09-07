# [H] Apache NiFi GetAsanaObject Processor has Remote Code Execution via Unsafe Deserialization

## Summary
Severity: High
Advisory: GHSA-v4p2-2w39-mhrj
CVE: CVE-2025-66524
CWE: CWE-502
Ecosystem: Maven
CVSS: CVSS:4.0/AV:N/AC:H/AT:P/PR:H/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N/AU:Y/R:U/V:C/RE:L/U:Green (CVSS_V4)
Published: 2025-12-19
Source: https://github.com/advisories/GHSA-v4p2-2w39-mhrj
Type: github-advisory

## Affected
- Maven: `org.apache.nifi:nifi-asana-processors` — affected >=1.20.0 <2.7.0

## Details
Apache NiFi 1.20.0 through 2.6.0 include the GetAsanaObject Processor, which requires integration with a configurable Distribute Map Cache Client Service for storing and retrieving state information. The GetAsanaObject Processor used generic Java Object serialization and deserialization without filtering. Unfiltered Java object deserialization does not provide protection against crafted state information stored in the cache server configured for GetAsanaObject. Exploitation requires an Apache NiFi system running with the GetAsanaObject Processor, and direct access to the configured cache server. Upgrading to Apache NiFi 2.7.0 is the recommended mitigation, which replaces Java Object serialization with JSON serialization. Removing the GetAsanaObject Processor located in the nifi-asana-processors-nar bundle also prevents exploitation.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-66524
- https://github.com/apache/nifi/commit/1c081c15544b8459d69daaae2056f0f433cafce6
- https://github.com/apache/nifi
- https://lists.apache.org/thread/k9h004ydjg7opdvxr0nfywtzf33z60d7
- http://www.openwall.com/lists/oss-security/2025/12/18/2
