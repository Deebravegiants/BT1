# [C] Exposure of sensitive information in Apache Ozone

## Summary
Severity: Critical
Advisory: GHSA-3w5h-x4rh-hc28
CVE: CVE-2021-39231
CWE: CWE-668, CWE-862
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2021-11-23
Source: https://github.com/advisories/GHSA-3w5h-x4rh-hc28
Type: github-advisory

## Affected
- Maven: `org.apache.ozone:ozone-main` — affected >=0 <1.2.0

## Details
In Apache Ozone versions prior to 1.2.0, Various internal server-to-server RPC endpoints are available for connections, making it possible for an attacker to download raw data from Datanode and Ozone manager and modify Ratis replication configuration.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-39231
- https://github.com/apache/ozone
- https://mail-archives.apache.org/mod_mbox/ozone-dev/202111.mbox/%3C110cd117-75ed-364b-cd38-3effd20f2183%40apache.org%3E
- http://www.openwall.com/lists/oss-security/2021/11/19/2
