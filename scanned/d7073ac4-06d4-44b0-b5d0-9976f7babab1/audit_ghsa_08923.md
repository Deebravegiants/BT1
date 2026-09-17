# [H] Apache Neethi is vulnerable to a Denial of Service attack through algorithmic complexity in policy normalization

## Summary
Severity: High
Advisory: GHSA-g36m-9g3m-2vmp
CVE: CVE-2026-42402
CWE: CWE-400
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-05-01
Source: https://github.com/advisories/GHSA-g36m-9g3m-2vmp
Type: github-advisory

## Affected
- Maven: `org.apache.neethi:neethi` — affected >=0 <3.2.2

## Details
Apache Neethi is vulnerable to a Denial of Service attack through algorithmic complexity in policy normalization. Specially crafted WS-Policy documents can trigger an exponential Cartesian cross-product expansion during the normalization process, causing unbounded memory allocation that exhausts the JVM heap. This occurs when the normalization process generates an excessive number of policy alternatives without bounds, leading to runtime memory exhaustion.

Users should upgrade to 3.2.2 which limits the maximum number of normalized policy alternatives.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-42402
- https://github.com/apache/ws-neethi
- https://lists.apache.org/thread/p826j0phhmr9f83wzpmys1y0bdfrr2q4
- http://www.openwall.com/lists/oss-security/2026/05/01/6
