# [H] Incorrect Authorization in Getahead Direct Web Remoting

## Summary
Severity: High
Advisory: GHSA-384c-gg34-g96h
CVE: CVE-2007-0184
CWE: CWE-863
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2022-05-01
Source: https://github.com/advisories/GHSA-384c-gg34-g96h
Type: github-advisory

## Affected
- Maven: `org.directwebremoting:dwr` — affected >=0 <1.1.4

## Details
Getahead Direct Web Remoting (DWR) before 1.1.4 allows attackers to obtain unauthorized access to public methods via a crafted request that bypasses the include/exclude checks.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2007-0184
- https://exchange.xforce.ibmcloud.com/vulnerabilities/31377
- http://lists.opensuse.org/opensuse-security-announce/2009-02/msg00002.html
