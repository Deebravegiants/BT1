# [H] Apache Helix Front (UI) component contained a hard-coded secret

## Summary
Severity: High
Advisory: GHSA-6247-7862-q2pq
CVE: CVE-2024-22281
CWE: CWE-668
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2024-08-21
Source: https://github.com/advisories/GHSA-6247-7862-q2pq
Type: github-advisory

## Affected
- Maven: `org.apache.helix:helix` — affected >=0

## Details
The Apache Helix Front (UI) component contained a hard-coded secret, allowing an attacker to spoof sessions by generating their own fake cookies.

This issue affects Apache Helix Front (UI): all versions.

As this project is retired, we do not plan to release a version that fixes this issue. Users are recommended to find an alternative or restrict access to the instance to trusted users.

NOTE: This vulnerability only affects products that are no longer supported by the maintainer.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-22281
- https://github.com/apache/helix
- https://lists.apache.org/thread/zt26fpmrqx3fzcy8nv3b43kb3xllo5ny
- http://www.openwall.com/lists/oss-security/2024/08/20/3
